from time import sleep
import datetime, os, subprocess  


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    manu()

def hisoblash():
    try:
        num1 = float(input("Birinchi sonni kiriting: "))
        num2 = float(input("Ikkinchi sonni kiriting: "))
        operator = input("Amalni tanlang (+, -, *, /): ")
        
        if operator == '+':
            result = num1 + num2
        elif operator == '-':
            result = num1 - num2
        elif operator == '*':
            result = num1 * num2
        elif operator == '/':
            if num2 != 0:
                result = num1 / num2
            else:
                print("Nolga bo'lish mumkin emas.")
                return
        else:
            print("Noto'g'ri amal tanlandi.")
            return
        
        print(f"Natija: {result}")
    except ValueError:
        print("Iltimos, sonlarni to'g'ri kiriting.")
    manu()

def delet_file():
    file_name = input("O'chirmoqchi bo'lgan fayl nomini kiriting: ")
    if os.path.exists(file_name):
        os.remove(file_name)
        uyqu()
        print(f"{file_name} fayli o'chirildi.")
    else:
        print(f"{file_name} fayli topilmadi.")
    manu()
    
def vaqt():
    now = datetime.datetime.now()
    print("Hozirgi vaqt: ", now.strftime("%Y-%m-%d %H:%M"))
    manu()

def uyqu():
    print("Bir sonia kuting...")
    sleep(1)

def och():
    openfile =input(str("file nomini kriting masalan: 'file.txt' --> : "))
    if openfile == "chiqish":
        print("Dasturdan chiqildi.")
        manu()
    else:
        with open(openfile, 'r') as file:
            data = file.read()
            print(data)
    manu()
    

def yoz():
    openfile =input(str("file nomini kriting masalan: 'file.txt' --> : "))
    with open(openfile, 'w') as file:
        data = input("Yozmoqchi bo'lgan matningizni kiriting: ")
        file.write(data)
    with open(openfile, 'r') as file:
        data = file.read()
        print("Yozilgan matn: ", data)
    manu()

def file_qoshish():
    openfile =input(str("file nomini kriting masalan: 'file.txt' --> : "))
    with open(openfile, 'a') as file:
        data = input("Qo'shmoqchi bo'lgan matningizni kiriting: ")
        file.write(data)
    with open(openfile, 'r') as file:
        data = file.read()
        print("Yozilgan matn: ", data)
    manu()

def matin():
    print("1. Faylni ochish")
    print("2. Faylga yozish")
    print("3. Fayl qo'shish")
    print("4. File o'chirish")
    print("5. Ilova ochish")
    print("6. Vaqt")
    print("7. Hisoblash")
    print("8. Tozalash")
    print("9. Chiqish")

def tanlov():
    i = input("Kerakli raqamni tanlang: ")
    if i=='1':
        uyqu()
        och()
    elif i=='2':
        uyqu()
        yoz()
    elif i=='3':
        uyqu()
        file_qoshish()
    elif i=='4':
        uyqu()
        delet_file()
    elif i=='5':
        uyqu()
        ilova_ochish()
    elif i=='6':
        uyqu()
        vaqt()
    elif i=='7':
        uyqu()
        hisoblash()
    elif i=='8':
        clear_screen()
        print("Tozalandi.")
    elif i=='9':
        uyqu()
        print("Dasturdan chiqildi.")
    else:
        uyqu()
        print("Noto'g'ri raqam, qayta urinib ko'ring.") 

def manu():
    matin()
    tanlov()
          
manu()