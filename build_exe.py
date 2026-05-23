# -*- coding: utf-8 -*-
import os
import sys
import subprocess

def run_command(cmd):
    print(f"실행 중: {cmd}")
    result = subprocess.run(cmd, shell=True, text=True)
    return result.returncode

def main():
    print("===================================================")
    print("   통합 소켓 시뮬레이터 EXE 빌드 스크립트")
    print("===================================================")
    
    # 1. PyInstaller 설치 상태 확인
    try:
        import PyInstaller
        print("PyInstaller가 이미 설치되어 있습니다.")
    except ImportError:
        print("PyInstaller가 설치되어 있지 않습니다. 설치를 진행합니다...")
        # uv 검출 시도 후 설치
        try:
            subprocess.run("uv --version", shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("uv를 사용하여 PyInstaller를 설치합니다.")
            run_command("uv pip install pyinstaller")
        except Exception:
            print("pip를 사용하여 PyInstaller를 설치합니다.")
            run_command(f'"{sys.executable}" -m pip install pyinstaller')

    # 2. PyInstaller를 사용하여 socket_sim_total.py 빌드
    # sys.executable을 사용하여 현재 가상환경의 python 모듈로서 PyInstaller를 실행함으로써 환경 혼선을 방지합니다.
    build_cmd = f'"{sys.executable}" -m PyInstaller --noconsole --onefile --clean --name="Socket_Simulator_Total" socket_sim_total.py'
    
    print("\n빌드 작업을 시작합니다. 완료될 때까지 잠시만 기다려 주세요...")
    ret = run_command(build_cmd)
    
    if ret == 0:
        print("\n===================================================")
        print("빌드가 성공적으로 완료되었습니다!")
        print("생성된 파일: dist/Socket_Simulator_Total.exe")
        print("===================================================")
    else:
        print("\n===================================================")
        print("빌드 도중 에러가 발생했습니다. 로그를 확인하세요.")
        print("===================================================")

if __name__ == "__main__":
    main()
