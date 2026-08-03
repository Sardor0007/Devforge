import os
import json
import subprocess
import urllib.request
import urllib.parse
from django.conf import settings

class DockerSandboxExecutor:
    def __init__(self, workspace_pk, timeout=60):
        self.workspace_pk = workspace_pk
        self.timeout = timeout
        self.workspace_dir = settings.BASE_DIR / 'workspaces' / str(workspace_pk)
        
    def _is_docker_available(self):
        """Docker buyruqlar satrining mavjudligini va ishlayotganini tekshiradi"""
        try:
            res = subprocess.run(['docker', 'info'], capture_output=True, text=True, timeout=3)
            return res.returncode == 0
        except Exception:
            return False

    def execute_in_docker(self, cmd, language="python"):
        """Docker konteynerida buyruqni xavfsiz bajarish"""
        # Konteyner sozlamalari va rasmlari
        lang_images = {
            "python": "python:3.10-slim",
            "javascript": "node:18-alpine",
            "cpp": "gcc:11",
            "c": "gcc:11",
        }
        image = lang_images.get(language, "python:3.10-slim")
        
        # Windowsda pathni moslashtirish (docker mount uchun)
        host_path = str(self.workspace_dir.resolve())
        container_path = "/usr/src/app"
        
        # Resurs limitlari bilan xavfsiz docker run buyrug'ini tuzamiz
        docker_cmd = [
            'docker', 'run', '--rm',
            '-v', f"{host_path}:{container_path}",
            '-w', container_path,
            '--memory', '128m',
            '--cpus', '0.5',
            '--network', 'none',  # Internet taqiqlanadi
            image,
            'sh', '-c', cmd
        ]
        
        try:
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr
            return {
                'output': output,
                'exit_code': result.returncode,
                'success': result.returncode == 0,
                'method': 'docker'
            }
        except subprocess.TimeoutExpired:
            return {
                'output': f"⏳ Buyruq bajarilish vaqti tugadi ({self.timeout}s). Limit oshib ketdi.",
                'exit_code': -1,
                'success': False,
                'method': 'docker'
            }
        except Exception as e:
            return {
                'output': f"Docker xatolik: {str(e)}",
                'exit_code': -1,
                'success': False,
                'method': 'docker'
            }

    def execute_in_piston(self, filename, content, language="python"):
        """Piston remote sandbox API orqali kodni bajarish"""
        piston_url = "https://emkc.org/api/v2/piston/execute"
        
        lang_map = {
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "java": "java",
            "cpp": "cpp",
            "c": "c",
            "cs": "csharp",
            "go": "go",
            "rs": "rust",
            "php": "php",
            "rb": "ruby",
            "sh": "bash",
            "bash": "bash"
        }
        
        # Fayl kengaytmasidan tilni aniqlaymiz
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        piston_lang = lang_map.get(ext, language)
        
        payload = {
            "language": piston_lang,
            "version": "*",
            "files": [
                {
                    "name": filename,
                    "content": content or ""
                }
            ]
        }
        
        try:
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
                return {
                    'output': output or "✓ Kod xatosiz bajarildi (output bo'sh)",
                    'exit_code': run_info.get('code', 0),
                    'success': run_info.get('code', 0) == 0 and not compile_info.get('stderr'),
                    'method': 'piston'
                }
        except Exception as e:
            return {
                'output': f"Piston API xatoligi: {str(e)}",
                'exit_code': -1,
                'success': False,
                'method': 'piston'
            }

    def execute_locally(self, cmd):
        """Piston API yoki Docker bo'lmaganda yoki 401 xatosi berganda local subprocess orqali bajarish"""
        try:
            env = dict(os.environ)
            mingw_bin = r"C:\Users\sardo\AppData\Local\Microsoft\WinGet\Packages\BrechtSanders.WinLibs.POSIX.UCRT_Microsoft.Winget.Source_8wekyb3d8bbwe\mingw64\bin"
            if os.path.isdir(mingw_bin) and mingw_bin not in env.get('PATH', ''):
                env['PATH'] = mingw_bin + os.pathsep + env.get('PATH', '')

            result = subprocess.run(
                cmd,
                shell=True,
                cwd=str(self.workspace_dir.resolve()),
                capture_output=True,
                text=True,
                env=env,
                timeout=60
            )
            output = result.stdout
            if result.stderr:
                output += ("\n" if output else "") + result.stderr
            return {
                'output': output or "✓ Kod bajarildi (output bo'sh)",
                'exit_code': result.returncode,
                'success': result.returncode == 0,
                'method': 'local'
            }
        except subprocess.TimeoutExpired:
            return {
                'output': "⏳ Buyruq bajarilish vaqti tugadi (60s limit).",
                'exit_code': -1,
                'success': False,
                'method': 'local'
            }
        except Exception as e:
            return {
                'output': f"Local ijro xatoligi: {str(e)}",
                'exit_code': -1,
                'success': False,
                'method': 'local'
            }

    def run(self, cmd, filename=None, file_content=None, language="python"):
        """Docker -> Piston API -> Local Subprocess fallback execution strategy."""
        # 1. Docker mavjud bo'lsa, xavfsiz konteynerda bajarish
        if self._is_docker_available():
            return self.execute_in_docker(cmd, language)
            
        # 2. Remote Piston API orqali bajarish
        if filename:
            piston_res = self.execute_in_piston(filename, file_content or '', language)
            if piston_res.get('exit_code') != -1 and 'Piston API xatoligi' not in piston_res.get('output', ''):
                return piston_res

        # 3. Local fallback (Piston 401/error berganda yoki ulanib bo'lmaganda)
        return self.execute_locally(cmd)
