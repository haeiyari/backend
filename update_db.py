#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
데이터베이스 업데이트 스크립트
Dump20251114.sql 파일을 실행하여 데이터베이스를 업데이트합니다.
"""

import mysql.connector
from mysql.connector import Error
import os

# 데이터베이스 설정
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',  # MySQL 비밀번호를 입력하세요
    'database': 'shopping_app',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def execute_sql_file(filename):
    """SQL 파일을 읽어서 실행"""
    try:
        print(f"📂 SQL 파일 읽는 중: {filename}")
        
        # SQL 파일 읽기
        with open(filename, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 데이터베이스 연결
        print("🔌 데이터베이스 연결 중...")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # SQL 문을 세미콜론으로 분리하여 실행
        sql_commands = sql_content.split(';')
        
        print(f"⚙️  총 {len(sql_commands)}개의 SQL 명령 실행 중...")
        
        executed = 0
        for command in sql_commands:
            command = command.strip()
            
            # 빈 명령이나 주석만 있는 경우 건너뛰기
            if not command or command.startswith('--') or command.startswith('/*'):
                continue
            
            try:
                cursor.execute(command)
                executed += 1
                
                # 진행 상황 표시 (매 50개마다)
                if executed % 50 == 0:
                    print(f"   ✓ {executed}개 명령 실행 완료...")
                    
            except Error as e:
                # 일부 명령은 실패해도 계속 진행 (예: 이미 존재하는 인덱스)
                if "Duplicate" not in str(e) and "already exists" not in str(e):
                    print(f"   ⚠️  경고: {str(e)[:100]}")
        
        connection.commit()
        print(f"\n✅ 데이터베이스 업데이트 완료! (총 {executed}개 명령 실행)")
        
        cursor.close()
        connection.close()
        
        return True
        
    except FileNotFoundError:
        print(f"❌ 오류: SQL 파일을 찾을 수 없습니다: {filename}")
        return False
    except Error as e:
        print(f"❌ 데이터베이스 오류: {e}")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return False

def main():
    """메인 함수"""
    print("=" * 60)
    print("🗄️  데이터베이스 업데이트 스크립트")
    print("=" * 60)
    print()
    
    # SQL 파일 경로
    sql_file = "Dump20251114.sql"
    
    if not os.path.exists(sql_file):
        print(f"❌ 오류: {sql_file} 파일이 없습니다.")
        print(f"   현재 디렉토리: {os.getcwd()}")
        return
    
    # 사용자 확인
    print(f"📋 실행할 파일: {sql_file}")
    print(f"🎯 대상 데이터베이스: {DB_CONFIG['database']}")
    print()
    
    response = input("계속 진행하시겠습니까? (y/n): ")
    
    if response.lower() != 'y':
        print("❌ 취소되었습니다.")
        return
    
    print()
    
    # SQL 파일 실행
    success = execute_sql_file(sql_file)
    
    if success:
        print()
        print("=" * 60)
        print("✨ 업데이트 내용:")
        print("   - users 테이블에 소셜 로그인 컬럼 추가")
        print("   - products 테이블에 FULLTEXT 인덱스 추가")
        print("   - password_reset_tokens 테이블 생성")
        print("=" * 60)
        print()
        print("🎉 모든 작업이 완료되었습니다!")
    else:
        print()
        print("❌ 업데이트 중 오류가 발생했습니다.")

if __name__ == "__main__":
    main()

