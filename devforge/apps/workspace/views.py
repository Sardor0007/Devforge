from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.conf import settings
import json
from apps.accounts.models import User
from apps.projects.models import Project
from .models import Workspace, WorkspaceFile, ChatRoom, ChatMessage


# ─── VIEWS ───────────────────────────────────────────────────────────────────
@login_required
def workspace_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    is_member = project.members.filter(user=request.user, is_approved=True).exists()
    is_creator = project.creator == request.user

    if not (is_member or is_creator):
        messages.error(request, "Bu ish maydoniga kirish uchun loyiha a'zosi bo'lishingiz kerak.")
        return redirect('project_detail', pk=pk)

    workspace, _ = Workspace.objects.get_or_create(project=project)
    files = workspace.files.all()
    chat_room, _ = ChatRoom.objects.get_or_create(project=project)
    messages_qs = chat_room.messages.select_related('sender').order_by('-created_at')[:50]

    # Auto-open a specific file (e.g. when arriving from feed integration)
    auto_open_file = None
    open_file_id = request.GET.get('open_file')
    if open_file_id:
        try:
            auto_open_file = workspace.files.get(pk=int(open_file_id))
        except (WorkspaceFile.DoesNotExist, ValueError):
            pass
    # If no explicit file, auto-open the first file (e.g. newly created snippet)
    if auto_open_file is None:
        auto_open_file = workspace.files.filter(is_folder=False).order_by('created_at').first()

    return render(request, 'workspace/workspace.html', {
        'project': project,
        'workspace': workspace,
        'files': files,
        'chat_room': chat_room,
        'chat_messages': reversed(list(messages_qs)),
        'members': project.members.filter(is_approved=True).select_related('user'),
        'auto_open_file': auto_open_file,
    })



@login_required
@require_POST
def file_create_view(request, workspace_pk):
    workspace = get_object_or_404(Workspace, pk=workspace_pk)
    data = json.loads(request.body)
    name = data.get('name', 'untitled.py')
    path = data.get('path', '/')
    language = data.get('language', 'python')

    f, created = WorkspaceFile.objects.get_or_create(
        workspace=workspace, name=name, path=path,
        defaults={'language': language, 'created_by': request.user}
    )
    
    # WebSocket Broadcast
    broadcast_file_change(workspace.id, 'create', f.pk, f.name, f.path, request.user.username)

    return JsonResponse({'id': f.pk, 'name': f.name, 'created': created})


@login_required
@require_POST
def file_save_view(request, file_pk):
    f = get_object_or_404(WorkspaceFile, pk=file_pk)
    data = json.loads(request.body)
    f.content = data.get('content', '')
    f.save()

    # WebSocket Broadcast
    broadcast_file_change(f.workspace.id, 'save', f.pk, f.name, f.path, request.user.username)

    return JsonResponse({
        'status': 'saved',
        'updated_at': f.updated_at.timestamp()
    })


@login_required
def file_load_view(request, file_pk):
    f = get_object_or_404(WorkspaceFile, pk=file_pk)
    is_bin = bool(f.binary_file)
    return JsonResponse({
        'content': f.content if not is_bin else '',
        'language': f.language,
        'name': f.name,
        'is_binary': is_bin,
        'updated_at': f.updated_at.timestamp()
    })


@login_required
def file_raw_view(request, file_pk):
    """Faylni asl ko'rinishida (raw) qaytaradi (3D loaderlar uchun)"""
    f = get_object_or_404(WorkspaceFile, pk=file_pk)
    if f.binary_file:
        return HttpResponse(f.binary_file.read(), content_type="application/octet-stream")
    return HttpResponse(f.content, content_type="text/plain; charset=utf-8")


def broadcast_file_change(workspace_id, action, file_id, name, path, sender_username):
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"workspace_{workspace_id}",
                {
                    "type": "file_change",
                    "action": action,
                    "file_id": file_id,
                    "name": name,
                    "path": path,
                    "sender": sender_username
                }
            )
    except Exception as e:
        print(f"WS broadcast file change error: {e}")


@login_required
@require_POST
def chat_message_view(request, room_pk):
    room = get_object_or_404(ChatRoom, pk=room_pk)
    content = request.POST.get('content', '').strip()
    if content:
        msg = ChatMessage.objects.create(room=room, sender=request.user, content=content)
        
        # WebSocket Broadcast to Workspace Group
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            channel_layer = get_channel_layer()
            if channel_layer:
                workspace_id = room.project.workspace.id
                async_to_sync(channel_layer.group_send)(
                    f"workspace_{workspace_id}",
                    {
                        "type": "workspace_chat",
                        "data": {
                            "type": "chat_message",
                            "id": msg.pk,
                            "sender": msg.sender.username,
                            "content": msg.content,
                            "time": msg.created_at.strftime('%H:%M'),
                        }
                    }
                )
        except Exception as e:
            print(f"Workspace chat WS broadcast error: {e}")

        return JsonResponse({
            'id': msg.pk,
            'sender': msg.sender.username,
            'content': msg.content,
            'time': msg.created_at.strftime('%H:%M'),
        })
    return JsonResponse({'error': 'Bo\'sh xabar'}, status=400)


@login_required
def chat_messages_view(request, room_pk):
    room = get_object_or_404(ChatRoom, pk=room_pk)
    last_id = request.GET.get('last_id', 0)
    msgs = room.messages.filter(pk__gt=last_id).select_related('sender')
    return JsonResponse({'messages': [
        {'id': m.pk, 'sender': m.sender.username, 'content': m.content,
         'time': m.created_at.strftime('%H:%M')} for m in msgs
    ]})





# ─── TERMINAL ─────────────────────────────────────────────────────────────────
import subprocess, os, signal, threading, time
from django.views.decorators.csrf import csrf_exempt

# Har bir workspace uchun joriy ishchi papkani saqlaymiz (server xotirasi)
_cwd_store = {}  # workspace_pk -> cwd path

# Interaktiv terminal sessiyalari
_terminal_sessions = {} # workspace_pk -> TerminalSession

class TerminalSession:
    def __init__(self, cmd, cwd, env, workspace_pk):
        self.workspace_pk = workspace_pk
        self.output_buffer = []
        self.lock = threading.Lock()
        self.process = subprocess.Popen(
            cmd,
            shell=True,
            cwd=cwd,
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1, # Line buffered
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        self.active = True
        self.last_seen = time.time()
        self.timestamp = time.time()

        # Output o'quvchi threadlar
        self.stdout_thread = threading.Thread(target=self._reader, args=(self.process.stdout,), daemon=True)
        self.stderr_thread = threading.Thread(target=self._reader, args=(self.process.stderr,), daemon=True)
        self.stdout_thread.start()
        self.stderr_thread.start()

    def _reader(self, pipe):
        fd = pipe.fileno()
        while self.active:
            try:
                # Read chunks up to 1024 bytes (blocks until at least 1 byte is available)
                data = os.read(fd, 1024)
                if not data:
                    break
                text = data.decode('utf-8', errors='ignore')
                with self.lock:
                    self.output_buffer.append(text)
                self.last_seen = time.time()
            except Exception:
                break
        pipe.close()

    def send_input(self, text):
        if self.process.poll() is None:
            try:
                self.process.stdin.write(text + '\n')
                self.process.stdin.flush()
                self.last_seen = time.time()
            except Exception:
                pass

    def get_output(self):
        with self.lock:
            out = "".join(self.output_buffer)
            self.output_buffer = []
            return out

    def is_alive(self):
        return self.process.poll() is None

    def stop(self):
        self.active = False
        if self.is_alive():
            if os.name == 'nt':
                self.process.terminate()
            else:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
        try:
            self.process.stdin.close()
            self.process.stdout.close()
            self.process.stderr.close()
        except Exception:
            pass

# Windows uchun MinGW (g++, gcc) yo'lini PATH ga qo'shamiz
_MINGW_BIN = r"C:\Users\sardo\AppData\Local\Microsoft\WinGet\Packages\BrechtSanders.WinLibs.POSIX.UCRT_Microsoft.Winget.Source_8wekyb3d8bbwe\mingw64\bin"

def _build_env(workspace_pk=None):
    """Subprocess uchun PATH ga MinGW qo'shilgan environment qaytaradi"""
    env = dict(os.environ)
    current_path = env.get('PATH', '')
    if _MINGW_BIN not in current_path and os.path.isdir(_MINGW_BIN):
        env['PATH'] = _MINGW_BIN + os.pathsep + current_path
    
    # Lokal paketlarni (pip --target packages) PYTHONPATHga qo'shish
    if workspace_pk:
        root_dir = settings.BASE_DIR / 'workspaces' / str(workspace_pk)
        pkg_dir = str(root_dir / 'packages')
        if os.path.exists(pkg_dir):
            current_pp = env.get('PYTHONPATH', '')
            env['PYTHONPATH'] = pkg_dir + (os.pathsep + current_pp if current_pp else '')

    env['TERM'] = 'xterm-256color'
    env['FORCE_COLOR'] = '0'
    return env

BLOCKED_COMMANDS = [
    'rm -rf /', 'rm -rf ~', 'mkfs', 'dd if=/dev/zero',
    ':(){:|:&};:', 'chmod -R 777 /', 'chown -R',
    'shutdown', 'reboot', 'halt', 'poweroff',
    'sudo ', 'su ', 'passwd', 'useradd', 'userdel',
    'groupadd', 'groupdel', 'visudo', 'crontab',
    'apt ', 'yum ', 'dnf ', 'pacman ', 'systemctl',
    'ssh ', 'scp ', 'ftp ',
    '/etc/', '/var/', '/root', '/bin/', '/sbin/',
    '$HOME', '..',
]

def is_blocked(cmd):
    cmd_lower = cmd.lower().strip()
    # Check for basic blocked commands
    if any(b in cmd_lower for b in BLOCKED_COMMANDS):
        return True
    
    # Preventing access outside workspace using absolute paths or parent directory tokens
    # Note: '..' is already in BLOCKED_COMMANDS, but we can be more specific
    if '..' in cmd or cmd.startswith('/') or (':' in cmd and '\\' in cmd):
        # Allow it only if it's within handling for cd or specific allowed commands
        # But for general commands like 'cat /etc/passwd', we block.
        pass

    return False


def _virtualize_path(path, workspace_pk):
    """Real yo'lni 'virtual' yo'lga aylantiradi (rootdirni olib tashlaydi)"""
    if not path:
        return "~"
    root_dir = str(settings.BASE_DIR / 'workspaces' / str(workspace_pk))
    
    # Normalizatsiya (bir xil slashlar va h.k.)
    path = os.path.normpath(path)
    root_dir = os.path.normpath(root_dir)
    
    if path.startswith(root_dir):
        # Rootni olib tashlash va faqat nisbiy qismini qoldirish
        virtual = path[len(root_dir):].replace('\\', '/')
        return "~" + (virtual if virtual.startswith('/') else '/' + virtual)
    
    # Agar rootdan tashqarida bo'lsa (teoretik bo'lmasligi kerak), shunchaki oxirgi qismi
    return "~/" + os.path.basename(path)


@login_required
@require_POST
def terminal_run_view(request, workspace_pk):
    """Terminal buyrug'ini bajaradi va natijani qaytaradi"""
    workspace = get_object_or_404(Workspace, pk=workspace_pk)
    project   = workspace.project

    # Faqat a'zolar ishlatishi mumkin
    is_member  = project.members.filter(user=request.user, is_approved=True).exists()
    is_creator = project.creator == request.user
    if not (is_member or is_creator):
        return JsonResponse({'output': "Ruxsat yo'q", 'error': True}, status=403)

    data = json.loads(request.body)
    cmd  = data.get('cmd', '').strip()

    if not cmd:
        return JsonResponse({'output': '', 'cwd': _get_cwd(workspace_pk)})

    # Xavfli buyruqlarni bloklash
    if is_blocked(cmd):
        return JsonResponse({
            'output': f'⛔ Xavfli buyruq bloklandi: {cmd}',
            'error': True,
            'cwd': _get_cwd(workspace_pk),
        })

    # cd buyrug'ini alohida boshqaramiz
    if cmd.startswith('cd '):
        return _handle_cd(workspace_pk, cmd)

    # Fayllarni diskka sinxronlash (agar run/python kabi buyruq bo'lsa)
    _sync_workspace_to_disk(workspace)

    cwd = _get_cwd(workspace_pk)

    # C++ KOMPILYATSIYA/BAJARISH (Windows Device Guard aylanib o'tish uchun remote fallback)
    if "g++" in cmd:
        import re
        cpp_match = re.search(r'"([^"]+\.cpp)"', cmd) or re.search(r'([^\s]+\.cpp)', cmd)
        if cpp_match:
            cpp_file_name = os.path.basename(cpp_match.group(1))
            try:
                wf = WorkspaceFile.objects.filter(workspace=workspace, name=cpp_file_name, is_folder=False).first()
                if wf:
                    import urllib.request
                    piston_url = "https://emkc.org/api/v2/piston/execute"
                    payload = {
                        "language": "cpp",
                        "version": "*",
                        "files": [
                            {
                                "name": wf.name,
                                "content": wf.content
                            }
                        ]
                    }
                    req = urllib.request.Request(
                        piston_url,
                        data=json.dumps(payload).encode('utf-8'),
                        headers={'Content-Type': 'application/json'},
                        method='POST'
                    )
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        res_data = json.loads(resp.read().decode('utf-8'))
                        run_info = res_data.get('run', {})
                        output = run_info.get('output', '')
                        compile_info = res_data.get('compile', {})
                        if compile_info.get('output'):
                            output = compile_info.get('output') + "\n" + output
                        return JsonResponse({
                            'output': output or '',
                            'exit_code': run_info.get('code', 0),
                            'error': run_info.get('code', 0) != 0 or bool(compile_info.get('stderr')),
                            'cwd': _virtualize_path(cwd, workspace_pk),
                        })
            except Exception:
                pass
    
    # Sandbox Executor orqali kodni to'g'ridan-to mezoniy bajarish
    filename = data.get('filename')
    file_content = data.get('file_content')
    language = data.get('language', 'python')

    import re
    if not filename:
        file_match = re.search(r'([a-zA-Z0-9_\-\.]+\.(py|js|cpp|c|go|rs|ts|java|cs|php|rb|sh|bash))', cmd)
        filename = file_match.group(1) if file_match else None
    
    if filename and not file_content:
        from apps.workspace.models import WorkspaceFile
        wf = WorkspaceFile.objects.filter(workspace=workspace, name=os.path.basename(filename), is_folder=False).first()
        if wf:
            file_content = wf.content

    try:
        from apps.workspace.sandbox import DockerSandboxExecutor
        executor = DockerSandboxExecutor(workspace_pk)
        exec_res = executor.run(cmd, filename=filename, file_content=file_content, language=language)
        
        output = exec_res['output']
        root_dir = str(settings.BASE_DIR / 'workspaces' / str(workspace_pk))
        if output:
            output = output.replace(root_dir, "~")
            output = output.replace(root_dir.replace('\\', '/'), "~")

        return JsonResponse({
            'output': output or '',
            'exit_code': exec_res['exit_code'],
            'error': not exec_res['success'],
            'cwd': _virtualize_path(cwd, workspace_pk),
        })
    except Exception as e:
        error_msg = str(e)
        root_dir = str(settings.BASE_DIR / 'workspaces' / str(workspace_pk))
        error_msg = error_msg.replace(root_dir, "~")

        return JsonResponse({
            'output': f"Bajarishda xatolik: {error_msg}",
            'error': True,
            'cwd': _virtualize_path(cwd, workspace_pk),
        })


def _sync_workspace_to_disk(workspace):
    """Barcha fayllarni database dan real diskka yozadi (faqat o'zgarganlarini)"""
    base_dir = settings.BASE_DIR / 'workspaces' / str(workspace.pk)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir, exist_ok=True)
    
    for f in workspace.files.all():
        rel_path = f.path.strip('/')
        file_dir = base_dir / rel_path
        if not os.path.exists(file_dir):
            os.makedirs(file_dir, exist_ok=True)
        
        if not f.is_folder:
            file_path = file_dir / f.name
            content = f.content or ''
            
            # Agar fayl allaqachon mavjud bo'lsa va kontenti bir xil bo'lsa, yozishni o'tkazib yuboramiz
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as fs:
                        if fs.read() == content:
                            continue
                except Exception:
                    pass
            
            with open(file_path, 'w', encoding='utf-8') as fs:
                fs.write(content)


def _get_cwd(workspace_pk):
    if workspace_pk not in _cwd_store:
        _cwd_store[workspace_pk] = str(settings.BASE_DIR / 'workspaces' / str(workspace_pk))
    cwd = _cwd_store[workspace_pk]
    if not os.path.exists(cwd):
        os.makedirs(cwd, exist_ok=True)
        _cwd_store[workspace_pk] = cwd
    return _cwd_store[workspace_pk]


def _handle_cd(workspace_pk, cmd):
    root_dir = str(settings.BASE_DIR / 'workspaces' / str(workspace_pk))
    cwd = _get_cwd(workspace_pk)
    
    parts = cmd.split(None, 1)
    target = parts[1] if len(parts) > 1 else '~'
    
    if target == '~':
        target = root_dir
    else:
        # Expand user and normalize
        target = os.path.expanduser(target)
        if not os.path.isabs(target):
            target = os.path.join(cwd, target)
        target = os.path.normpath(target)

    # SECRECY CHECK: Ensure the target is within the root_dir
    try:
        # On Windows, drive letters must match. commonpath works for this.
        if os.path.commonpath([root_dir, target]) != root_dir:
            return JsonResponse({
                'output': "⛔ Ruxsat yo'q: Ish maydonidan tashqariga chiqish taqiqlangan.\n",
                'error': True,
                'cwd': cwd,
            })
    except Exception:
        return JsonResponse({
            'output': "⛔ Noto'g'ri yo'l.\n",
            'error': True,
            'cwd': cwd,
        })

    if os.path.isdir(target):
        _cwd_store[workspace_pk] = target
        return JsonResponse({'output': '', 'cwd': _virtualize_path(target, workspace_pk)})
    else:
        # Xatodagi real yo'lni yashirish
        virtual_target = _virtualize_path(target, workspace_pk)
        return JsonResponse({
            'output': f"cd: {virtual_target}: Bunday papka yo'q\n",
            'error': True,
            'cwd': _virtualize_path(cwd, workspace_pk),
        })


@login_required
@require_POST
def terminal_input_view(request, workspace_pk):
    session = _terminal_sessions.get(workspace_pk)
    if not session or not session.is_alive():
        return JsonResponse({'error': 'Sessiya faol emas'}, status=400)
    
    data = json.loads(request.body)
    text = data.get('text', '')
    session.send_input(text)
    return JsonResponse({'status': 'ok'})


@login_required
def terminal_poll_view(request, workspace_pk):
    session = _terminal_sessions.get(workspace_pk)
    if not session:
        return JsonResponse({'output': '', 'is_alive': False})
    
    output = session.get_output()
    alive = session.is_alive()
    
    # Virtualize paths in output
    root_dir = str(settings.BASE_DIR / 'workspaces' / str(workspace_pk))
    output = output.replace(root_dir, "~").replace(root_dir.replace('\\', '/'), "~")
    
    if not alive:
        # Sessiyani tozalash
        del _terminal_sessions[workspace_pk]

    return JsonResponse({
        'output': output,
        'is_alive': alive
    })


@login_required
@require_POST
def terminal_stop_view(request, workspace_pk):
    session = _terminal_sessions.get(workspace_pk)
    if session:
        session.stop()
        del _terminal_sessions[workspace_pk]
        return JsonResponse({'status': 'stopped'})
    return JsonResponse({'status': 'not_running'})


@login_required
def terminal_cwd_view(request, workspace_pk):
    """Joriy papkani qaytaradi"""
    get_object_or_404(Workspace, pk=workspace_pk)
    return JsonResponse({'cwd': _virtualize_path(_get_cwd(workspace_pk), workspace_pk)})


# ─── PAPKA BOSHQARUV ─────────────────────────────────────────────────────────

@login_required
@require_POST
def folder_create_view(request, workspace_pk):
    """Yangi papka yaratish"""
    workspace = get_object_or_404(Workspace, pk=workspace_pk)
    _check_access(request.user, workspace)
    data = json.loads(request.body)
    name = data.get('name', '').strip().replace('/', '_')
    path = data.get('path', '/')
    if not name:
        return JsonResponse({'error': 'Nom kerak'}, status=400)
    folder, created = WorkspaceFile.objects.get_or_create(
        workspace=workspace, name=name, path=path,
        defaults={'is_folder': True, 'created_by': request.user}
    )
    
    # WebSocket Broadcast
    broadcast_file_change(workspace.id, 'create_folder', folder.pk, folder.name, folder.path, request.user.username)

    return JsonResponse({'id': folder.pk, 'name': folder.name, 'path': folder.path, 'created': created})


@login_required
@require_POST
def file_delete_view(request, file_pk):
    """Fayl yoki papkani o'chirish"""
    f = get_object_or_404(WorkspaceFile, pk=file_pk)
    _check_access(request.user, f.workspace)
    workspace_id = f.workspace.id
    file_id = f.pk
    file_name = f.name
    file_path = f.path
    
    if f.is_folder:
        # Papka ichidagi barcha fayllarni o'chirish
        full = f.full_path()
        WorkspaceFile.objects.filter(
            workspace=f.workspace,
            path__startswith=full
        ).delete()
    f.delete()
    
    # WebSocket Broadcast
    broadcast_file_change(workspace_id, 'delete', file_id, file_name, file_path, request.user.username)

    return JsonResponse({'status': 'deleted'})


@login_required
@require_POST
def file_rename_view(request, file_pk):
    """Fayl yoki papkani qayta nomlash"""
    f    = get_object_or_404(WorkspaceFile, pk=file_pk)
    _check_access(request.user, f.workspace)
    data = json.loads(request.body)
    new_name = data.get('name', '').strip().replace('/', '_')
    if not new_name:
        return JsonResponse({'error': 'Nom kerak'}, status=400)
    old_full = f.full_path()
    f.name = new_name
    f.save(update_fields=['name'])
    # Papka bo'lsa ichidagi fayllar path ni yangilash
    if f.is_folder:
        new_full = f.full_path()
        children = WorkspaceFile.objects.filter(
            workspace=f.workspace,
            path__startswith=old_full
        )
        for child in children:
            child.path = child.path.replace(old_full, new_full, 1)
            child.save(update_fields=['path'])
            
    # WebSocket Broadcast
    broadcast_file_change(f.workspace.id, 'rename', f.pk, f.name, f.path, request.user.username)

    return JsonResponse({'id': f.pk, 'name': f.name})


@login_required
def file_tree_view(request, workspace_pk):
    """To'liq fayl daraxti JSON ko'rinishida"""
    workspace = get_object_or_404(Workspace, pk=workspace_pk)
    _check_access(request.user, workspace)
    files = workspace.files.all().values(
        'id', 'name', 'path', 'language', 'is_folder',
        'file_size', 'updated_at'
    )
    return JsonResponse({'files': list(files)})


# ─── FAYL YUKLASH (LOCAL) ─────────────────────────────────────────────────────

@login_required
@require_POST
def file_upload_view(request, workspace_pk):
    """Localdan bir yoki ko'p fayl yuklash"""
    workspace = get_object_or_404(Workspace, pk=workspace_pk)
    _check_access(request.user, workspace)

    uploaded = []
    errors   = []

    for key in request.FILES:
        f = request.FILES[key]
        # relative_path header orqali keladi (papka yuklashda)
        rel_path = request.POST.get(f'path_{key}', '/').strip() or '/'
        name     = f.name
        size     = f.size

        # Fayl hajmi 5MB dan oshmasin
        if size > 5 * 1024 * 1024:
            errors.append(f'{name}: 5MB dan katta')
            continue

        # Kontent o'qish (Binary yoki Text)
        ext = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
        binary_exts = ['glb', 'gltf', 'obj', 'fbx', 'stl', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'exe', 'bin']
        is_bin = ext in binary_exts

        content = ''
        binary_file = None
        
        if is_bin:
            binary_file = f
        else:
            try:
                content = f.read().decode('utf-8', errors='replace')
            except Exception:
                content = ''

        lang_map = {
            'py':'python','js':'javascript','ts':'javascript',
            'html':'html','css':'css','json':'json',
            'md':'markdown','txt':'text','glsl':'glsl',
            'cs':'csharp','cpp':'cpp','c':'c','h':'c',
            'sh':'bash','yaml':'yaml','yml':'yaml',
        }
        language = lang_map.get(ext, 'text')

        # Papkani avval yaratish
        if rel_path != '/':
            _ensure_folders(workspace, rel_path, request.user)

        wf, created = WorkspaceFile.objects.update_or_create(
            workspace=workspace, name=name, path=rel_path,
            defaults={
                'content':     content,
                'binary_file': binary_file,
                'language':    language,
                'file_size':   size,
                'is_folder':   False,
                'created_by':  request.user,
            }
        )
        uploaded.append({'id': wf.pk, 'name': wf.name, 'path': wf.path, 'language': language, 'is_binary': is_bin})

    return JsonResponse({'uploaded': uploaded, 'errors': errors})


def _ensure_folders(workspace, path, user):
    """Papka yo'lini rekursiv yaratish: /src/components → src, src/components"""
    parts = [p for p in path.strip('/').split('/') if p]
    current = '/'
    for part in parts:
        WorkspaceFile.objects.get_or_create(
            workspace=workspace, name=part, path=current,
            defaults={'is_folder': True, 'created_by': user}
        )
        current = f'{current.rstrip("/")}/{part}'


def _check_access(user, workspace):
    """Workspace ga kirish huquqini tekshirish"""
    project    = workspace.project
    is_creator = project.creator == user
    is_member  = project.members.filter(user=user, is_approved=True).exists()
    if not (is_creator or is_member):
        from django.http import Http404
        raise Http404


# ─── GITHUB INTEGRATSIYA ──────────────────────────────────────────────────────

import urllib.request as urllib_req
import urllib.parse

def _get_github_token(user):
    """Foydalanuvchining GitHub OAuth tokenini olish"""
    try:
        from allauth.socialaccount.models import SocialToken, SocialApp
        token = SocialToken.objects.filter(
            account__user=user,
            account__provider='github'
        ).select_related('app').first()
        return token.token if token else None
    except Exception:
        return None


def _github_api(endpoint, token):
    """GitHub API ga so'rov"""
    import urllib.request, json as _json
    url = f'https://api.github.com{endpoint}'
    req = urllib.request.Request(url, headers={
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'DevForge/1.0',
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return _json.loads(resp.read().decode())
    except Exception as e:
        return {'error': str(e)}


@login_required
def github_repos_view(request):
    """Foydalanuvchining GitHub repolarini olish"""
    token = _get_github_token(request.user)
    if not token:
        return JsonResponse({
            'error': 'GitHub akkount ulangan emas',
            'connect_url': '/accounts/github/login/?process=connect'
        }, status=400)

    data = _github_api('/user/repos?per_page=50&sort=updated&type=all', token)
    if 'error' in data:
        return JsonResponse({'error': data['error']}, status=500)

    repos = [{
        'id':          r['id'],
        'name':        r['name'],
        'full_name':   r['full_name'],
        'description': r.get('description', '') or '',
        'private':     r['private'],
        'language':    r.get('language', '') or '',
        'updated_at':  r['updated_at'][:10],
        'default_branch': r.get('default_branch', 'main'),
        'url':         r['html_url'],
    } for r in data if isinstance(r, dict) and 'id' in r]

    return JsonResponse({'repos': repos})


@login_required
def github_tree_view(request):
    """Repo fayl daraxti"""
    token     = _get_github_token(request.user)
    if not token:
        return JsonResponse({'error': 'GitHub ulangan emas'}, status=400)

    repo      = request.GET.get('repo', '')
    branch    = request.GET.get('branch', 'main')
    path      = request.GET.get('path', '')

    if not repo:
        return JsonResponse({'error': 'repo parametri kerak'}, status=400)

    if path:
        endpoint = f'/repos/{repo}/contents/{path}?ref={branch}'
    else:
        endpoint = f'/repos/{repo}/contents?ref={branch}'

    data = _github_api(endpoint, token)

    if isinstance(data, dict) and 'error' in data:
        return JsonResponse({'error': data['error']}, status=500)

    if isinstance(data, dict) and 'message' in data:
        return JsonResponse({'error': data['message']}, status=400)

    if isinstance(data, dict):
        # Bitta fayl
        items = [data]
    else:
        items = data

    files = [{
        'name':         item['name'],
        'path':         item['path'],
        'type':         item['type'],       # file | dir
        'size':         item.get('size', 0),
        'sha':          item.get('sha', ''),
        'download_url': item.get('download_url', ''),
    } for item in items if isinstance(item, dict)]

    # Papkalar oldin
    files.sort(key=lambda x: (0 if x['type'] == 'dir' else 1, x['name'].lower()))

    return JsonResponse({'files': files, 'repo': repo, 'branch': branch, 'path': path})


@login_required
@require_POST
def github_import_view(request, workspace_pk):
    """GitHub dan fayl(lar)ni workspace ga import qilish"""
    workspace = get_object_or_404(Workspace, pk=workspace_pk)
    _check_access(request.user, workspace)

    token = _get_github_token(request.user)
    if not token:
        return JsonResponse({'error': 'GitHub ulangan emas'}, status=400)

    data         = json.loads(request.body)
    repo         = data.get('repo', '')
    branch       = data.get('branch', 'main')
    items        = data.get('items', [])   # [{path, type, sha, name}]
    target_path  = data.get('target_path', '/')

    if not items:
        return JsonResponse({'error': 'Fayllar tanlanmagan'}, status=400)

    imported = []
    errors   = []

    for item in items:
        try:
            if item['type'] == 'dir':
                # Papkani rekursiv import
                _import_github_dir(
                    workspace, token, repo, branch,
                    item['path'], target_path, request.user, imported, errors
                )
            else:
                _import_github_file(
                    workspace, token, repo, branch,
                    item['path'], item['name'], target_path,
                    item.get('sha', ''), request.user, imported, errors
                )
        except Exception as e:
            errors.append(f"{item.get('name','?')}: {str(e)}")

    return JsonResponse({'imported': imported, 'errors': errors, 'count': len(imported)})


def _import_github_file(workspace, token, repo, branch, gh_path, name, target_path, sha, user, imported, errors):
    """Bitta GitHub faylni workspace ga import"""
    import urllib.request, base64

    endpoint = f'/repos/{repo}/contents/{gh_path}?ref={branch}'
    data = _github_api(endpoint, token)

    if 'error' in data or 'message' in data:
        errors.append(f"{name}: {data.get('error') or data.get('message')}")
        return

    # Content decode
    encoding = data.get('encoding', '')
    content  = ''
    if encoding == 'base64':
        try:
            raw = base64.b64decode(data['content'].replace('\n', '').replace('\r', ''))
            content = raw.decode('utf-8', errors='replace')
        except Exception:
            content = ''

    ext      = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
    lang_map = {
        'py':'python','js':'javascript','ts':'javascript',
        'html':'html','css':'css','json':'json','md':'markdown',
        'txt':'text','glsl':'glsl','cs':'csharp','cpp':'cpp',
        'c':'c','h':'c','sh':'bash','yaml':'yaml','yml':'yaml',
    }
    language = lang_map.get(ext, 'text')
    size     = data.get('size', 0)

    wf, _ = WorkspaceFile.objects.update_or_create(
        workspace=workspace, name=name, path=target_path,
        defaults={
            'content':    content,
            'language':   language,
            'file_size':  size,
            'github_sha': sha,
            'is_folder':  False,
            'created_by': user,
        }
    )
    imported.append({'id': wf.pk, 'name': name, 'path': target_path})


def _import_github_dir(workspace, token, repo, branch, gh_path, target_base, user, imported, errors):
    """GitHub papkasini rekursiv import"""
    dir_name    = gh_path.split('/')[-1]
    folder_path = f'{target_base.rstrip("/")}/{dir_name}'

    # Papka yaratish
    WorkspaceFile.objects.get_or_create(
        workspace=workspace,
        name=dir_name,
        path=target_base,
        defaults={'is_folder': True, 'created_by': user}
    )

    # Papka mazmunini olish
    data = _github_api(f'/repos/{repo}/contents/{gh_path}?ref={branch}', token)
    if not isinstance(data, list):
        errors.append(f"{dir_name}: papka mazmunini olishda xato")
        return

    for item in data:
        if item['type'] == 'dir':
            _import_github_dir(
                workspace, token, repo, branch,
                item['path'], folder_path, user, imported, errors
            )
        else:
            _import_github_file(
                workspace, token, repo, branch,
                item['path'], item['name'], folder_path,
                item.get('sha', ''), user, imported, errors
            )

# ─── PACKAGE MANAGER ──────────────────────────────────────────────────────────

@login_required
@require_POST
def package_install_view(request, workspace_pk):
    """Kutubxona o'rnatish (pip)"""
    workspace = get_object_or_404(Workspace, pk=workspace_pk)
    _check_access(request.user, workspace)
    
    data = json.loads(request.body)
    package_name = data.get('package', '').strip()
    
    if not package_name:
        return JsonResponse({'error': 'Kutubxona nomi kerak'}, status=400)
    
    # Xavfsizlik: faqat harf, raqam, chiziqcha va nuqta
    import re
    if not re.match(r'^[a-zA-Z0-9\-_.]+$', package_name):
        return JsonResponse({'error': 'Noto\'g\'ri kutubxona nomi'}, status=400)

    # Local packages papkasi
    cwd = _get_cwd(workspace_pk)
    target_dir = os.path.join(cwd, 'packages')
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)

    try:
        # pip install --target orqali localga o'rnatish
        # --no-cache-dir va --quiet ishlatamiz
        cmd = f'python -m pip install "{package_name}" --target "{target_dir}" --no-cache-dir'
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
            env=_build_env(workspace_pk),
        )
        
        output = result.stdout + (result.stderr or "")
        success = result.returncode == 0
        
        if success:
            return JsonResponse({
                'output': f'✅ {package_name} muvaffaqiyatli o\'rnatildi.\nEslatma: Kodda import qilishdan oldin sys.path ga "packages" papkasini qo\'shing.',
                'success': True
            })
        else:
            # Outputdagi real yo'llarni yashirish
            root_dir = str(settings.BASE_DIR / 'workspaces' / str(workspace_pk))
            output = output.replace(root_dir, "~").replace(root_dir.replace('\\', '/'), "~")
            
            return JsonResponse({
                'output': f'❌ O\'rnatishda xatolik:\n{output}',
                'success': False
            })
            
    except subprocess.TimeoutExpired:
        return JsonResponse({'error': 'O\'rnatish vaqti tugadi (60s)'}, status=504)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
