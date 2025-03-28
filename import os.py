import os
import shutil

# 원본 및 대상 디렉토리 설정
src_dir = "/home/johyunsuk/Downloads/choschos"
dst_dir = "/home/johyunsuk/Downloads/choschoschos"

# 대상 디렉토리가 없으면 생성
os.makedirs(dst_dir, exist_ok=True)

# 변경할 파일 범위 설정
start_old, end_old = 381, 500  # 기존 파일 이름 범위
start_new, end_new = 381, 500  # 새로운 파일 이름 범위

# 파일 이름을 변경하여 복사
for old_num, new_num in zip(range(start_old, end_old + 1), range(start_new, end_new + 1)):
    old_name = f"{old_num}.jpg"
    new_name = f"{new_num}_addsharpenedbroken.jpg"
    
    old_path = os.path.join(src_dir, old_name)
    new_path = os.path.join(dst_dir, new_name)
    
    # 파일이 존재하면 복사 및 이름 변경
    if os.path.exists(old_path):
        shutil.copy2(old_path, new_path)
        print(f"Copied: {old_path} -> {new_path}")
    else:
        print(f"Skipping: {old_path} (file not found)")

print("파일 이름 변경 및 복사 완료!")
