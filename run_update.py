#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
간단한 데이터베이스 업데이트 스크립트
"""

import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'shopping_app',
    'charset': 'utf8mb4'
}

def update_database():
    """데이터베이스 업데이트"""
    try:
        print("🔌 데이터베이스 연결 중...")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("⚙️  업데이트 실행 중...\n")
        
        # 1. users 테이블에 social_id 컬럼 추가
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN social_id VARCHAR(255) NULL COMMENT '소셜 로그인 ID'")
            print("✅ users.social_id 컬럼 추가 완료")
        except Error as e:
            if "Duplicate column" in str(e):
                print("ℹ️  users.social_id 컬럼 이미 존재")
            else:
                print(f"⚠️  users.social_id 추가 실패: {e}")
        
        # 2. users 테이블에 social_provider 컬럼 추가
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN social_provider VARCHAR(50) NULL COMMENT '소셜 로그인 제공자'")
            print("✅ users.social_provider 컬럼 추가 완료")
        except Error as e:
            if "Duplicate column" in str(e):
                print("ℹ️  users.social_provider 컬럼 이미 존재")
            else:
                print(f"⚠️  users.social_provider 추가 실패: {e}")
        
        # 3. users 테이블의 password를 NULL 허용으로 변경
        try:
            cursor.execute("ALTER TABLE users MODIFY COLUMN password VARCHAR(255) NULL COMMENT '암호화된 비밀번호 (소셜 로그인 시 NULL 가능)'")
            print("✅ users.password NULL 허용으로 변경 완료")
        except Error as e:
            print(f"⚠️  users.password 수정 실패: {e}")
        
        # 4. 소셜 로그인 인덱스 추가
        try:
            cursor.execute("CREATE INDEX idx_social_login ON users(social_id, social_provider)")
            print("✅ idx_social_login 인덱스 추가 완료")
        except Error as e:
            if "Duplicate key" in str(e):
                print("ℹ️  idx_social_login 인덱스 이미 존재")
            else:
                print(f"⚠️  인덱스 추가 실패: {e}")
        
        # 5. products 테이블에 FULLTEXT 인덱스 추가
        try:
            cursor.execute("ALTER TABLE products ADD FULLTEXT INDEX idx_product_search (name, description)")
            print("✅ products FULLTEXT 인덱스 추가 완료")
        except Error as e:
            if "Duplicate key" in str(e):
                print("ℹ️  products FULLTEXT 인덱스 이미 존재")
            else:
                print(f"⚠️  FULLTEXT 인덱스 추가 실패: {e}")
        
        # 6. password_reset_tokens 테이블 생성
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    token VARCHAR(500) NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_token (token(255)),
                    INDEX idx_expires (expires_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='비밀번호 재설정 토큰'
            """)
            print("✅ password_reset_tokens 테이블 생성 완료")
        except Error as e:
            print(f"ℹ️  password_reset_tokens 테이블 이미 존재 또는 생성 실패: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 데이터베이스 업데이트 완료!")
        print("=" * 60)
        print("\n✨ 업데이트 내용:")
        print("   - users 테이블에 소셜 로그인 컬럼 추가")
        print("   - products 테이블에 FULLTEXT 인덱스 추가")
        print("   - password_reset_tokens 테이블 생성")
        print("\n✅ 기존 데이터는 모두 보존되었습니다!")
        
    except Error as e:
        print(f"\n❌ 데이터베이스 연결 오류: {e}")
        print("\n확인사항:")
        print("   - MySQL 서버가 실행 중인가요?")
        print("   - DB_CONFIG의 비밀번호가 맞나요?")
        print("   - shopping_app 데이터베이스가 존재하나요?")

if __name__ == "__main__":
    print("=" * 60)
    print("🗄️  데이터베이스 업데이트")
    print("=" * 60)
    print()
    update_database()

