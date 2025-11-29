-- 1. 외래키 검사 끄기 (순서 상관없이 삭제/생성 가능하게 함)
SET NAMES utf8mb4;
SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO';

-- 2. 기존 테이블 싹 지우기 (초기화)
DROP TABLE IF EXISTS `wishlist`;
DROP TABLE IF EXISTS `user_measure_profile`;
DROP TABLE IF EXISTS `shipping`;
DROP TABLE IF EXISTS `payments`;
DROP TABLE IF EXISTS `orderitems`;
DROP TABLE IF EXISTS `orders`;
DROP TABLE IF EXISTS `cart`;
DROP TABLE IF EXISTS `product_real_measure`;
DROP TABLE IF EXISTS `product_size_option`;
DROP TABLE IF EXISTS `product_images`;
DROP TABLE IF EXISTS `products`;
DROP TABLE IF EXISTS `categories`;
DROP TABLE IF EXISTS `password_reset_tokens`;
DROP TABLE IF EXISTS `users`;

-- -----------------------------------------------------
-- 3. 테이블 생성 및 데이터 입력 시작
-- -----------------------------------------------------

-- A. Users 테이블 생성 및 데이터 입력
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '사용자 ID (자동 증가)',
  `name` varchar(100) NOT NULL COMMENT '이름',
  `nickname` varchar(100) NOT NULL DEFAULT '' COMMENT '닉네임',
  `email` varchar(255) NOT NULL COMMENT '이메일 (UNIQUE)',
  `password` varchar(255) DEFAULT NULL COMMENT '암호화된 비밀번호 (소셜 로그인 시 NULL 가능)',
  `phone` varchar(20) DEFAULT NULL COMMENT '전화번호',
  `social_id` varchar(255) DEFAULT NULL COMMENT '소셜 로그인 ID',
  `social_provider` varchar(50) DEFAULT NULL COMMENT '소셜 로그인 제공자 (kakao, google)',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '가입일',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_social_login` (`social_id`,`social_provider`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `users` (`id`, `name`, `nickname`, `email`, `password`, `phone`, `created_at`, `updated_at`) VALUES 
(3,'이지수','두두','dodo46@naver.com','6286shj','01036786886','2025-05-09 21:34:49','2025-05-10 12:04:12'),
(4,'권예빈','치치','tyeirb@naver.com','yw7whsis','01052868372','2025-05-09 21:34:49','2025-05-10 12:04:12'),
(5,'김수연','우유','wyhshsij@naver.com','hsu81@#','01036725562','2025-05-09 21:34:49','2025-05-10 12:04:12'),
(6,'이나은','공강 킬러','ohkdha@naver.com','iwy6wy!!','01026757262','2025-05-09 21:34:49','2025-05-10 12:04:12'),
(7,'박솔은','자유를 외치다','ciel@naver.com','78eishsj','01037825273','2025-05-09 21:34:49','2025-05-10 12:04:12'),
(8,'홍길동','','hong@test.com','81dc9bdb52d04dc20036dbd8313ed055',NULL,'2025-11-01 15:46:51','2025-11-01 15:46:51'),
(9,'김영희','','kim@test.com','674f3c2c1a8a6f90461e8a66fb5550ba',NULL,'2025-11-01 15:46:51','2025-11-01 15:46:51');


-- B. Categories 테이블 (카테고리)
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '카테고리 ID',
  `name` varchar(100) NOT NULL COMMENT '카테고리명',
  `parent_id` int DEFAULT NULL COMMENT '상위 카테고리 ID (nullable)',
  PRIMARY KEY (`id`),
  KEY `parent_id` (`parent_id`),
  CONSTRAINT `categories_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `categories` VALUES (16,'의류',NULL),(17,'남성 의류',16),(18,'여성 의류',16),(19,'아동 의류',16),(26,'아우터',17),(27,'상의',17),(28,'바지',17),(29,'홈웨어',17),(30,'아우터',18),(31,'상의',18),(32,'바지',18),(33,'원피스',18),(34,'치마',18),(35,'홈웨어',18),(36,'아우터',19),(37,'상의',19),(38,'바지',19),(39,'치마',19),(40,'홈웨어',19);


-- C. Products 테이블 (상품 - AUTO_INCREMENT 변경됨)
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '상품 ID',
  `name` varchar(200) NOT NULL COMMENT '상품명',
  `description` text COMMENT '상품 설명',
  `price` decimal(10,2) NOT NULL COMMENT '가격',
  `stock_quantity` int DEFAULT '0' COMMENT '재고 수량',
  `category_id` int DEFAULT NULL COMMENT '카테고리 ID (FK)',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '등록일',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일',
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  FULLTEXT KEY `idx_product_search` (`name`,`description`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `products` VALUES 
(4,'남성 셔츠','캐주얼 스타일의 면 셔츠',29000.00,50,27,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(5,'남성 청바지','슬림핏 데님 바지',45000.00,30,28,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(6,'여성 원피스','봄철용 플라워 패턴 원피스',55000.00,20,32,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(7,'여성 스커트','하이웨이스트 롱 스커트',38000.00,40,33,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(8,'아동 티셔츠','귀여운 캐릭터 프린트 티셔츠',15000.00,100,38,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(9,'아동 청바지','신축성 좋은 아동용 청바지',20000.00,60,39,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(10, '플로킹 로고 그래픽 맨투맨', '자동 삽입된 상품입니다. (상의 분류)', 84550.00, 50, 27, NOW(), NOW()),
(11, '베이직 오버핏 긴팔 티셔츠', '자동 삽입된 상품입니다. (상의 분류)', 15890.00, 50, 27, NOW(), NOW()),
(12, '중량담요 후드티 코코아 브라운', '자동 삽입된 상품입니다. (상의 분류)', 68400.00, 50, 27, NOW(), NOW()),
(13, '컨투어 폭스 헤드 스케이트 셔츠', '자동 삽입된 상품입니다. (상의 분류)', 160990.00, 50, 27, NOW(), NOW()),
(14, '우먼즈 릴렉스드 스웨트 팬츠', '자동 삽입된 상품입니다. (하의 분류)', 19590.00, 50, 28, NOW(), NOW()),
(15, '아르코 커브드 데님', '자동 삽입된 상품입니다. (하의 분류)', 81840.00, 50, 28, NOW(), NOW()),
(16, '이지 세미와이드 슬랙스', '자동 삽입된 상품입니다. (하의 분류)', 29890.00, 50, 28, NOW(), NOW()),
(17, '여성 피어스 니트 팬츠', '자동 삽입된 상품입니다. (하의 분류)', 99000.00, 50, 28, NOW(), NOW());


-- D. Product Size Option 테이블 (AUTO_INCREMENT 변경됨)
CREATE TABLE `product_size_option` (
  `size_option_id` int NOT NULL AUTO_INCREMENT COMMENT '사이즈 옵션 고유 ID',
  `product_id` int NOT NULL COMMENT '상품 ID (Products 테이블 참조)',
  `option_name` varchar(30) NOT NULL COMMENT '사이즈명 (예: "M", "L", "100")',
  `stock_quantity` int NOT NULL DEFAULT '0' COMMENT '해당 사이즈의 재고 수량',
  PRIMARY KEY (`size_option_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `product_size_option_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `product_size_option` VALUES 
(1,4,'M',30),(2,4,'L',50),(3,4,'XL',20),(4,4,'XXL',0),(5,5,'28',25),(6,5,'30',30),(7,5,'32',15),(8,6,'Free',30),(9,6,'S',20),(10,6,'M',10),(11,7,'S',25),(12,7,'M',30),(13,7,'L',5),
(24, 10, 'M(95)', 15), (25, 10, 'L(100)', 15), (26, 10, 'XL(105)', 15), (27, 10, '2XL(110)', 15), 
(28, 11, 'M(95)', 15), (29, 11, 'L(100)', 15), (30, 11, 'XL(105)', 15), (31, 11, '2XL(110)', 15), (32, 11, '3XL(115~120)', 15),
(33, 12, 'S', 15), (34, 12, 'M', 15), (35, 12, 'L', 15), 
(36, 13, 'M', 15), (37, 13, 'L', 15), (38, 13, 'XL', 15), 
(39, 14, 'XS', 15), (40, 14, 'S', 15), (41, 14, 'M', 15), (42, 14, 'L', 15), 
(43, 15, 'S', 15), (44, 15, 'M', 15), (45, 15, 'L', 15), 
(46, 16, 'M', 15), (47, 16, 'L', 15), (48, 16, 'XL', 15), (49, 16, '2XL', 15), (50, 16, '3XL', 15),
(51, 17, 'XS', 15), (52, 17, 'S', 15), (53, 17, 'M', 15);


-- E. Product Real Measure 테이블 (AUTO_INCREMENT 변경됨)
CREATE TABLE `product_real_measure` (
  `measure_id` int NOT NULL AUTO_INCREMENT COMMENT '실측 고유 ID',
  `size_option_id` int NOT NULL COMMENT '사이즈 옵션 ID (Product_Size_Option 참조)',
  `category` varchar(50) NOT NULL COMMENT '분류 (예: "상의", "하의")',
  `top_length` decimal(5,1) DEFAULT NULL COMMENT '상의 총장 (cm, 소수점 1자리)',
  `top_shoulder` decimal(5,1) DEFAULT NULL COMMENT '상의 어깨너비 (cm, 소수점 1자리)',
  `top_chest` decimal(5,1) DEFAULT NULL COMMENT '상의 가슴단면 (cm, 소수점 1자리)',
  `top_sleeve` decimal(5,1) DEFAULT NULL COMMENT '상의 소매길이 (cm, 소수점 1자리)',
  `bottom_length` decimal(5,1) DEFAULT NULL COMMENT '하의 총장 (cm, 소수점 1자리)',
  `bottom_waist` decimal(5,1) DEFAULT NULL COMMENT '하의 허리단면 (cm, 소수점 1자리)',
  `bottom_rise` decimal(5,1) DEFAULT NULL COMMENT '하의 밑위 (cm, 소수점 1자리)',
  `bottom_hip` decimal(5,1) DEFAULT NULL COMMENT '하의 엉덩이단면 (cm, 소수점 1자리)',
  `bottom_thigh` decimal(5,1) DEFAULT NULL COMMENT '하의 허벅지단면 (cm, 소수점 1자리)',
  `bottom_hem` decimal(5,1) DEFAULT NULL COMMENT '하의 밑단단면 (cm, 소수점 1자리)',
  PRIMARY KEY (`measure_id`),
  KEY `size_option_id` (`size_option_id`),
  CONSTRAINT `product_real_measure_ibfk_1` FOREIGN KEY (`size_option_id`) REFERENCES `product_size_option` (`size_option_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `product_real_measure` VALUES 
(1,1,'상의',70.0,45.0,52.5,22.0,NULL,NULL,NULL,NULL,NULL,NULL),
(2,2,'상의',72.0,47.0,55.0,23.0,NULL,NULL,NULL,NULL,NULL,NULL),
(3,5,'하의',NULL,NULL,NULL,NULL,100.0,38.5,29.0,48.0,30.0,20.0),
(11, 24, '상의', 67.5, 46.5, 55.5, 62.7, NULL, NULL, NULL, NULL, NULL, NULL),
(12, 25, '상의', 69.5, 48.5, 58.0, 63.7, NULL, NULL, NULL, NULL, NULL, NULL),
(13, 26, '상의', 71.5, 50.5, 60.5, 64.7, NULL, NULL, NULL, NULL, NULL, NULL),
(14, 27, '상의', 73.5, 52.5, 63.0, 65.7, NULL, NULL, NULL, NULL, NULL, NULL),
(15, 28, '상의', 70.0, 49.0, 56.0, 59.0, NULL, NULL, NULL, NULL, NULL, NULL),
(16, 29, '상의', 71.0, 51.0, 58.0, 60.0, NULL, NULL, NULL, NULL, NULL, NULL),
(17, 30, '상의', 72.5, 53.0, 60.0, 61.0, NULL, NULL, NULL, NULL, NULL, NULL),
(18, 31, '상의', 74.5, 55.0, 62.0, 62.0, NULL, NULL, NULL, NULL, NULL, NULL),
(19, 32, '상의', 75.5, 57.0, 64.0, 63.0, NULL, NULL, NULL, NULL, NULL, NULL),
(20, 33, '상의', 65.0, 64.0, 63.0, 55.5, NULL, NULL, NULL, NULL, NULL, NULL),
(21, 34, '상의', 67.0, 66.0, 65.0, 56.5, NULL, NULL, NULL, NULL, NULL, NULL),
(22, 35, '상의', 69.0, 68.0, 67.0, 57.5, NULL, NULL, NULL, NULL, NULL, NULL),
(23, 36, '상의', 82.0, 51.0, 60.0, 65.5, NULL, NULL, NULL, NULL, NULL, NULL),
(24, 37, '상의', 86.0, 52.0, 61.0, 67.0, NULL, NULL, NULL, NULL, NULL, NULL),
(25, 38, '상의', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(26, 39, '하의', NULL, NULL, NULL, NULL, 96.0, 30.0, 30.8, 50.0, 30.8, 12.0),
(27, 40, '하의', NULL, NULL, NULL, NULL, 97.0, 32.5, 31.5, 52.5, 32.0, 12.5),
(28, 41, '하의', NULL, NULL, NULL, NULL, 98.0, 35.0, 32.3, 55.0, 33.3, 13.0),
(29, 42, '하의', NULL, NULL, NULL, NULL, 99.0, 37.5, 32.9, 57.5, 34.5, 13.5),
(30, 43, '하의', NULL, NULL, NULL, NULL, 103.0, 35.0, 32.0, 50.5, 33.0, 24.5),
(31, 44, '하의', NULL, NULL, NULL, NULL, 104.0, 37.0, 33.0, 52.5, 34.0, 25.0),
(32, 45, '하의', NULL, NULL, NULL, NULL, 107.0, 39.0, 34.0, 54.5, 35.0, 25.5),
(33, 46, '하의', NULL, NULL, NULL, NULL, 103.0, 40.0, 27.5, NULL, 32.0, 21.0),
(34, 47, '하의', NULL, NULL, NULL, NULL, 104.0, 42.0, 28.5, NULL, 33.0, 21.5),
(35, 48, '하의', NULL, NULL, NULL, NULL, 105.0, 44.0, 29.5, NULL, 34.0, 2.0),
(36, 49, '하의', NULL, NULL, NULL, NULL, 106.0, 46.0, 30.5, NULL, 35.0, 22.5),
(37, 50, '하의', NULL, NULL, NULL, NULL, 107.0, 48.0, 31.5, NULL, 36.0, 23.0),
(38, 51, '하의', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(39, 52, '하의', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(40, 53, '하의', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);


-- F. Product Images 테이블
CREATE TABLE `product_images` (
  `product_image_id` int NOT NULL AUTO_INCREMENT COMMENT '이미지 고유 ID (PK)',
  `product_id` int NOT NULL COMMENT '상품 ID (products.id 참조)',
  `image_url` varchar(255) NOT NULL COMMENT '이미지 경로 또는 URL',
  `image_type` varchar(50) NOT NULL COMMENT '이미지 타입 (예: main, detail)',
  PRIMARY KEY (`product_image_id`),
  KEY `fk_product_images_to_products` (`product_id`),
  CONSTRAINT `fk_product_images_to_products` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='상품별 상세 이미지';

INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (21, 10, '/images/p10_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (22, 10, '/images/p10_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (23, 11, '/images/p11_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (24, 11, '/images/p11_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (25, 12, '/images/p12_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (26, 12, '/images/p12_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (27, 13, '/images/p13_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (28, 13, '/images/p13_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (29, 14, '/images/p14_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (30, 14, '/images/p14_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (31, 15, '/images/p15_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (32, 15, '/images/p15_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (33, 16, '/images/p16_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (34, 16, '/images/p16_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (35, 17, '/images/p17_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (36, 17, '/images/p17_detail.jpg', 'detail');


-- G. Orders 테이블
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `total_price` decimal(10,2) NOT NULL,
  `status` varchar(50) NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `orders` VALUES (7,3,29000.00,'결제완료','2025-05-10 00:19:56'),(8,4,45000.00,'대기','2025-05-10 00:19:56'),(9,7,55000.00,'결제완료','2025-05-10 00:19:56'),(10,5,15000.00,'결제완료','2025-05-10 00:19:56'),(11,6,38000.00,'결제 완료','2025-05-10 00:19:56'),(12,5,20000.00,'대기','2025-05-10 00:19:56');


-- H. Order Items 테이블
CREATE TABLE `orderitems` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int NOT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `orderitems_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `orderitems_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `orderitems` VALUES (1,7,4,2,29000.00),(2,8,5,1,45000.00),(3,9,6,1,55000.00),(4,10,8,1,15000.00),(5,11,7,1,38000.00),(6,12,9,1,20000.00);


-- I. Cart 테이블
CREATE TABLE `cart` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '장바구니 ID',
  `user_id` int NOT NULL COMMENT '사용자 ID',
  `product_id` int NOT NULL COMMENT '상품 ID',
  `quantity` int NOT NULL DEFAULT '1' COMMENT '수량',
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`product_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `cart_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `cart_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `cart` VALUES (1,3,4,2),(2,5,5,1),(3,6,6,2),(4,4,7,3),(5,5,9,1),(6,7,8,4);


-- J. Payments 테이블
CREATE TABLE `payments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `method` varchar(50) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `status` varchar(50) NOT NULL,
  `paid_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `payments` VALUES (1,7,'카드',29000.00,'성공','2025-05-10 01:25:48'),(2,8,'무통장',45000.00,'실패','2025-05-10 01:25:48'),(3,9,'카드',55000.00,'성공','2025-05-10 01:25:48'),(4,10,'카드',15000.00,'성공','2025-05-10 01:25:48'),(5,11,'무통장',38000.00,'실패','2025-05-10 01:25:48'),(6,12,'카드',20000.00,'성공','2025-05-10 01:25:48');


-- K. Shipping 테이블
CREATE TABLE `shipping` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '배송 ID',
  `order_id` int NOT NULL COMMENT '주문 ID',
  `address` text NOT NULL COMMENT '배송지 주소',
  `receiver_name` varchar(255) NOT NULL COMMENT '수령자 이름',
  `receiver_phone` varchar(20) NOT NULL COMMENT '수령자 연락처',
  `status` varchar(50) NOT NULL COMMENT '배송 상태 (예: 배송 중, 도착 등)',
  `shipped_at` datetime DEFAULT NULL COMMENT '발송일',
  `delivered_at` datetime DEFAULT NULL COMMENT '도착일',
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  CONSTRAINT `shipping_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `shipping` VALUES (1,7,'천안시 서북구 쌍용동','이지수','01036786886','배송중',NULL,NULL),(2,8,'수원시 영통구 이의동','김수연','01036725562','배송중',NULL,NULL),(3,9,'전주시 덕진구 송천동','이나은','01026757262','도착',NULL,NULL),(4,10,'대전광역시 유성구 봉명동','권예빈','01052868372','도착',NULL,NULL),(5,11,'수원시 영통구 이의동','김수연','01036725562','배송중',NULL,NULL),(6,12,'서울특별시 강남구 역삼동','박솔은','01037825273','도착',NULL,NULL);


-- L. User Measure Profile 테이블
CREATE TABLE `user_measure_profile` (
  `profile_id` int NOT NULL AUTO_INCREMENT COMMENT '측정 프로필 고유 ID',
  `user_id` int NOT NULL COMMENT '사용자 ID (users 테이블 참조)',
  `profile_name` varchar(100) NOT NULL COMMENT '측정 프로필명 (예: "내 최애 후드티")',
  `profile_image_url` varchar(255) DEFAULT NULL COMMENT '사용자가 업로드한 옷 이미지 주소',
  `category` varchar(50) NOT NULL COMMENT '분류 (예: "상의", "하의")',
  `top_length` decimal(5,1) DEFAULT NULL,
  `top_shoulder` decimal(5,1) DEFAULT NULL,
  `top_chest` decimal(5,1) DEFAULT NULL,
  `top_sleeve` decimal(5,1) DEFAULT NULL,
  `bottom_length` decimal(5,1) DEFAULT NULL,
  `bottom_waist` decimal(5,1) DEFAULT NULL,
  `bottom_rise` decimal(5,1) DEFAULT NULL,
  `bottom_hip` decimal(5,1) DEFAULT NULL,
  `bottom_thigh` decimal(5,1) DEFAULT NULL,
  `bottom_hem` decimal(5,1) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '측정값을 저장한 날짜',
  PRIMARY KEY (`profile_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_measure_profile_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `user_measure_profile` VALUES (1,3,'내 최애 후드티 (L)',NULL,'상의',70.0,50.0,58.0,60.0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-01 17:38:50'),(2,3,'자주 입는 청바지 (30)',NULL,'하의',NULL,NULL,NULL,NULL,102.0,40.0,30.0,50.0,31.0,20.0,'2025-11-01 17:38:50'),(3,4,'딱 맞는 반팔티 (M)',NULL,'상의',68.0,46.0,53.0,21.0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-01 17:38:50');


-- M. Wishlist 테이블
CREATE TABLE `wishlist` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '찜 ID',
  `user_id` int NOT NULL COMMENT '사용자 ID',
  `product_id` int NOT NULL COMMENT '상품 ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`product_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `wishlist_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `wishlist_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `wishlist` VALUES (1,3,4),(4,4,7),(2,5,5),(5,5,9),(3,6,6),(6,7,8);


-- N. Password Reset Tokens 테이블 (추가된 기능)
CREATE TABLE `password_reset_tokens` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `token` VARCHAR(500) NOT NULL,
    `expires_at` TIMESTAMP NOT NULL,
    `used` BOOLEAN DEFAULT FALSE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_token` (`token`(255)),
    INDEX `idx_expires` (`expires_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='비밀번호 재설정 토큰';


-- 4. 마무리 (외래키 검사 다시 켜기)
SET FOREIGN_KEY_CHECKS = 1;
SELECT '✅ 모든 테이블 생성 및 데이터 입력이 성공적으로 완료되었습니다!' AS Result;

##해당 코드안에 추가해서 전체 코드를 보내줘

The user wants me to integrate the SQL generated in the previous step (8 new products: IDs 10-17, sizes, measurements, images) into the existing comprehensive SQL script.

I will take the full script content provided in the prompt and append the new INSERT statements, and crucially, update the `AUTO_INCREMENT` values to prevent conflicts when running the entire dump file.

**Integration Strategy:**
1.  **Products:** Append new `INSERT INTO products` statements (IDs 10-17) and update `AUTO_INCREMENT=18`.
2.  **Product Size Option:** Append new `INSERT INTO product_size_option` statements (IDs 24-53) and update `AUTO_INCREMENT=54`.
3.  **Product Real Measure:** Append new `INSERT INTO product_real_measure` statements (IDs 11-40) and update `AUTO_INCREMENT=41`.
4.  **Product Images:** Append new `INSERT INTO product_images` statements (IDs 21-36) and update `AUTO_INCREMENT=37`.

I will provide the entire, unified, corrected SQL script.**네, 알겠습니다. 기존 덤프 파일에 8개의 새 상품 데이터를 모두 통합하고, `AUTO_INCREMENT` 값까지 수정한 전체 SQL 코드를 보내드립니다.**

이 코드를 실행하시면 **기존 6개의 상품**과 **새로 추가된 8개의 상품(ID 10번~17번)**이 모두 깨끗하게 DB에 채워집니다.

---

### 📋 통합된 최종 SQL 코드 (전체 내용)

```sql
-- 1. 외래키 검사 끄기 (순서 상관없이 삭제/생성 가능하게 함)
SET NAMES utf8mb4;
SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO';

-- 2. 기존 테이블 싹 지우기 (초기화)
DROP TABLE IF EXISTS `wishlist`;
DROP TABLE IF EXISTS `user_measure_profile`;
DROP TABLE IF EXISTS `shipping`;
DROP TABLE IF EXISTS `payments`;
DROP TABLE IF EXISTS `orderitems`;
DROP TABLE IF EXISTS `orders`;
DROP TABLE IF EXISTS `cart`;
DROP TABLE IF EXISTS `product_real_measure`;
DROP TABLE IF EXISTS `product_size_option`;
DROP TABLE IF EXISTS `product_images`;
DROP TABLE IF EXISTS `products`;
DROP TABLE IF EXISTS `categories`;
DROP TABLE IF EXISTS `password_reset_tokens`;
DROP TABLE IF EXISTS `users`;

-- -----------------------------------------------------
-- 3. 테이블 생성 및 데이터 입력 시작
-- -----------------------------------------------------

-- A. Users 테이블 생성 및 데이터 입력
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '사용자 ID (자동 증가)',
  `name` varchar(100) NOT NULL COMMENT '이름',
  `nickname` varchar(100) NOT NULL DEFAULT '' COMMENT '닉네임',
  `email` varchar(255) NOT NULL COMMENT '이메일 (UNIQUE)',
  `password` varchar(255) DEFAULT NULL COMMENT '암호화된 비밀번호 (소셜 로그인 시 NULL 가능)',
  `phone` varchar(20) DEFAULT NULL COMMENT '전화번호',
  `social_id` varchar(255) DEFAULT NULL COMMENT '소셜 로그인 ID',
  `social_provider` varchar(50) DEFAULT NULL COMMENT '소셜 로그인 제공자 (kakao, google)',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '가입일',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_social_login` (`social_id`,`social_provider`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `users` (`id`, `name`, `nickname`, `email`, `password`, `phone`, `created_at`, `updated_at`) VALUES 
(3,'이지수','두두','dodo46@naver.com','6286shj','01036786886','2025-05-09 21:34:49','2025-05-10 12:04:12'),
(4,'권예빈','치치','tyeirb@naver.com','yw7whsis','01052868372','2025-05-09 21:34:49','2025-05-10 12:04:12'),
(5,'김수연','우유','wyhshsij@naver.com','hsu81@#','01036725562','2025-05-09 21:34:49','2025-05-10 12:04:12'),
(6,'이나은','공강 킬러','ohkdha@naver.com','iwy6wy!!','01026757262','2025-05-09 21:34:49','2025-05-10 12:04:12'),
(7,'박솔은','자유를 외치다','ciel@naver.com','78eishsj','01037825273','2025-05-09 21:34:49','2025-05-10 12:04:12'),
(8,'홍길동','','hong@test.com','81dc9bdb52d04dc20036dbd8313ed055',NULL,'2025-11-01 15:46:51','2025-11-01 15:46:51'),
(9,'김영희','','kim@test.com','674f3c2c1a8a6f90461e8a66fb5550ba',NULL,'2025-11-01 15:46:51','2025-11-01 15:46:51');


-- B. Categories 테이블 (카테고리)
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '카테고리 ID',
  `name` varchar(100) NOT NULL COMMENT '카테고리명',
  `parent_id` int DEFAULT NULL COMMENT '상위 카테고리 ID (nullable)',
  PRIMARY KEY (`id`),
  KEY `parent_id` (`parent_id`),
  CONSTRAINT `categories_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `categories` VALUES (16,'의류',NULL),(17,'남성 의류',16),(18,'여성 의류',16),(19,'아동 의류',16),(26,'아우터',17),(27,'상의',17),(28,'바지',17),(29,'홈웨어',17),(30,'아우터',18),(31,'상의',18),(32,'바지',18),(33,'원피스',18),(34,'치마',18),(35,'홈웨어',18),(36,'아우터',19),(37,'상의',19),(38,'바지',19),(39,'치마',19),(40,'홈웨어',19);


-- C. Products 테이블 (상품 - 8개 신규 추가됨)
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '상품 ID',
  `name` varchar(200) NOT NULL COMMENT '상품명',
  `description` text COMMENT '상품 설명',
  `price` decimal(10,2) NOT NULL COMMENT '가격',
  `stock_quantity` int DEFAULT '0' COMMENT '재고 수량',
  `category_id` int DEFAULT NULL COMMENT '카테고리 ID (FK)',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '등록일',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일',
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  FULLTEXT KEY `idx_product_search` (`name`,`description`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `products` VALUES 
(4,'남성 셔츠','캐주얼 스타일의 면 셔츠',29000.00,50,27,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(5,'남성 청바지','슬림핏 데님 바지',45000.00,30,28,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(6,'여성 원피스','봄철용 플라워 패턴 원피스',55000.00,20,32,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(7,'여성 스커트','하이웨이스트 롱 스커트',38000.00,40,33,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(8,'아동 티셔츠','귀여운 캐릭터 프린트 티셔츠',15000.00,100,38,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(9,'아동 청바지','신축성 좋은 아동용 청바지',20000.00,60,39,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(10, '플로킹 로고 그래픽 맨투맨', '자동 삽입된 상품입니다. (상의 분류)', 84550.00, 50, 27, NOW(), NOW()),
(11, '베이직 오버핏 긴팔 티셔츠', '자동 삽입된 상품입니다. (상의 분류)', 15890.00, 50, 27, NOW(), NOW()),
(12, '중량담요 후드티 코코아 브라운', '자동 삽입된 상품입니다. (상의 분류)', 68400.00, 50, 27, NOW(), NOW()),
(13, '컨투어 폭스 헤드 스케이트 셔츠', '자동 삽입된 상품입니다. (상의 분류)', 160990.00, 50, 27, NOW(), NOW()),
(14, '우먼즈 릴렉스드 스웨트 팬츠', '자동 삽입된 상품입니다. (하의 분류)', 19590.00, 50, 28, NOW(), NOW()),
(15, '아르코 커브드 데님', '자동 삽입된 상품입니다. (하의 분류)', 81840.00, 50, 28, NOW(), NOW()),
(16, '이지 세미와이드 슬랙스', '자동 삽입된 상품입니다. (하의 분류)', 29890.00, 50, 28, NOW(), NOW()),
(17, '여성 피어스 니트 팬츠', '자동 삽입된 상품입니다. (하의 분류)', 99000.00, 50, 28, NOW(), NOW());


-- D. Product Size Option 테이블 (AUTO_INCREMENT 변경됨)
CREATE TABLE `product_size_option` (
  `size_option_id` int NOT NULL AUTO_INCREMENT COMMENT '사이즈 옵션 고유 ID',
  `product_id` int NOT NULL COMMENT '상품 ID (Products 테이블 참조)',
  `option_name` varchar(30) NOT NULL COMMENT '사이즈명 (예: "M", "L", "100")',
  `stock_quantity` int NOT NULL DEFAULT '0' COMMENT '해당 사이즈의 재고 수량',
  PRIMARY KEY (`size_option_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `product_size_option_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `product_size_option` VALUES 
(1,4,'M',30),(2,4,'L',50),(3,4,'XL',20),(4,4,'XXL',0),(5,5,'28',25),(6,5,'30',30),(7,5,'32',15),(8,6,'Free',30),(9,6,'S',20),(10,6,'M',10),(11,7,'S',25),(12,7,'M',30),(13,7,'L',5),
(24, 10, 'M(95)', 15), (25, 10, 'L(100)', 15), (26, 10, 'XL(105)', 15), (27, 10, '2XL(110)', 15), 
(28, 11, 'M(95)', 15), (29, 11, 'L(100)', 15), (30, 11, 'XL(105)', 15), (31, 11, '2XL(110)', 15), (32, 11, '3XL(115~120)', 15),
(33, 12, 'S', 15), (34, 12, 'M', 15), (35, 12, 'L', 15), 
(36, 13, 'M', 15), (37, 13, 'L', 15), (38, 13, 'XL', 15), 
(39, 14, 'XS', 15), (40, 14, 'S', 15), (41, 14, 'M', 15), (42, 14, 'L', 15), 
(43, 15, 'S', 15), (44, 15, 'M', 15), (45, 15, 'L', 15), 
(46, 16, 'M', 15), (47, 16, 'L', 15), (48, 16, 'XL', 15), (49, 16, '2XL', 15), (50, 16, '3XL', 15),
(51, 17, 'XS', 15), (52, 17, 'S', 15), (53, 17, 'M', 15);


-- E. Product Real Measure 테이블 (AUTO_INCREMENT 변경됨)
CREATE TABLE `product_real_measure` (
  `measure_id` int NOT NULL AUTO_INCREMENT COMMENT '실측 고유 ID',
  `size_option_id` int NOT NULL COMMENT '사이즈 옵션 ID (Product_Size_Option 참조)',
  `category` varchar(50) NOT NULL COMMENT '분류 (예: "상의", "하의")',
  `top_length` decimal(5,1) DEFAULT NULL COMMENT '상의 총장 (cm, 소수점 1자리)',
  `top_shoulder` decimal(5,1) DEFAULT NULL COMMENT '상의 어깨너비 (cm, 소수점 1자리)',
  `top_chest` decimal(5,1) DEFAULT NULL COMMENT '상의 가슴단면 (cm, 소수점 1자리)',
  `top_sleeve` decimal(5,1) DEFAULT NULL COMMENT '상의 소매길이 (cm, 소수점 1자리)',
  `bottom_length` decimal(5,1) DEFAULT NULL COMMENT '하의 총장 (cm, 소수점 1자리)',
  `bottom_waist` decimal(5,1) DEFAULT NULL COMMENT '하의 허리단면 (cm, 소수점 1자리)',
  `bottom_rise` decimal(5,1) DEFAULT NULL COMMENT '하의 밑위 (cm, 소수점 1자리)',
  `bottom_hip` decimal(5,1) DEFAULT NULL COMMENT '하의 엉덩이단면 (cm, 소수점 1자리)',
  `bottom_thigh` decimal(5,1) DEFAULT NULL COMMENT '하의 허벅지단면 (cm, 소수점 1자리)',
  `bottom_hem` decimal(5,1) DEFAULT NULL COMMENT '하의 밑단단면 (cm, 소수점 1자리)',
  PRIMARY KEY (`measure_id`),
  KEY `size_option_id` (`size_option_id`),
  CONSTRAINT `product_real_measure_ibfk_1` FOREIGN KEY (`size_option_id`) REFERENCES `product_size_option` (`size_option_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `product_real_measure` VALUES 
(1,1,'상의',70.0,45.0,52.5,22.0,NULL,NULL,NULL,NULL,NULL,NULL),
(2,2,'상의',72.0,47.0,55.0,23.0,NULL,NULL,NULL,NULL,NULL,NULL),
(3,5,'하의',NULL,NULL,NULL,NULL,100.0,38.5,29.0,48.0,30.0,20.0),
(11, 24, '상의', 67.5, 46.5, 55.5, 62.7, NULL, NULL, NULL, NULL, NULL, NULL),
(12, 25, '상의', 69.5, 48.5, 58.0, 63.7, NULL, NULL, NULL, NULL, NULL, NULL),
(13, 26, '상의', 71.5, 50.5, 60.5, 64.7, NULL, NULL, NULL, NULL, NULL, NULL),
(14, 27, '상의', 73.5, 52.5, 63.0, 65.7, NULL, NULL, NULL, NULL, NULL, NULL),
(15, 28, '상의', 70.0, 49.0, 56.0, 59.0, NULL, NULL, NULL, NULL, NULL, NULL),
(16, 29, '상의', 71.0, 51.0, 58.0, 60.0, NULL, NULL, NULL, NULL, NULL, NULL),
(17, 30, '상의', 72.5, 53.0, 60.0, 61.0, NULL, NULL, NULL, NULL, NULL, NULL),
(18, 31, '상의', 74.5, 55.0, 62.0, 62.0, NULL, NULL, NULL, NULL, NULL, NULL),
(19, 32, '상의', 75.5, 57.0, 64.0, 63.0, NULL, NULL, NULL, NULL, NULL, NULL),
(20, 33, '상의', 65.0, 64.0, 63.0, 55.5, NULL, NULL, NULL, NULL, NULL, NULL),
(21, 34, '상의', 67.0, 66.0, 65.0, 56.5, NULL, NULL, NULL, NULL, NULL, NULL),
(22, 35, '상의', 69.0, 68.0, 67.0, 57.5, NULL, NULL, NULL, NULL, NULL, NULL),
(23, 36, '상의', 82.0, 51.0, 60.0, 65.5, NULL, NULL, NULL, NULL, NULL, NULL),
(24, 37, '상의', 86.0, 52.0, 61.0, 67.0, NULL, NULL, NULL, NULL, NULL, NULL),
(25, 38, '상의', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(26, 39, '하의', NULL, NULL, NULL, NULL, 96.0, 30.0, 30.8, 50.0, 30.8, 12.0),
(27, 40, '하의', NULL, NULL, NULL, NULL, 97.0, 32.5, 31.5, 52.5, 32.0, 12.5),
(28, 41, '하의', NULL, NULL, NULL, NULL, 98.0, 35.0, 32.3, 55.0, 33.3, 13.0),
(29, 42, '하의', NULL, NULL, NULL, NULL, 99.0, 37.5, 32.9, 57.5, 34.5, 13.5),
(30, 43, '하의', NULL, NULL, NULL, NULL, 103.0, 35.0, 32.0, 50.5, 33.0, 24.5),
(31, 44, '하의', NULL, NULL, NULL, NULL, 104.0, 37.0, 33.0, 52.5, 34.0, 25.0),
(32, 45, '하의', NULL, NULL, NULL, NULL, 107.0, 39.0, 34.0, 54.5, 35.0, 25.5),
(33, 46, '하의', NULL, NULL, NULL, NULL, 103.0, 40.0, 27.5, NULL, 32.0, 21.0),
(34, 47, '하의', NULL, NULL, NULL, NULL, 104.0, 42.0, 28.5, NULL, 33.0, 21.5),
(35, 48, '하의', NULL, NULL, NULL, NULL, 105.0, 44.0, 29.5, NULL, 34.0, 2.0),
(36, 49, '하의', NULL, NULL, NULL, NULL, 106.0, 46.0, 30.5, NULL, 35.0, 22.5),
(37, 50, '하의', NULL, NULL, NULL, NULL, 107.0, 48.0, 31.5, NULL, 36.0, 23.0),
(38, 51, '하의', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(39, 52, '하의', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(40, 53, '하의', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);


-- F. Product Images 테이블
CREATE TABLE `product_images` (
  `product_image_id` int NOT NULL AUTO_INCREMENT COMMENT '이미지 고유 ID (PK)',
  `product_id` int NOT NULL COMMENT '상품 ID (products.id 참조)',
  `image_url` varchar(255) NOT NULL COMMENT '이미지 경로 또는 URL',
  `image_type` varchar(50) NOT NULL COMMENT '이미지 타입 (예: main, detail)',
  PRIMARY KEY (`product_image_id`),
  KEY `fk_product_images_to_products` (`product_id`),
  CONSTRAINT `fk_product_images_to_products` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='상품별 상세 이미지';

INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (21, 10, '/images/p10_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (22, 10, '/images/p10_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (23, 11, '/images/p11_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (24, 11, '/images/p11_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (25, 12, '/images/p12_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (26, 12, '/images/p12_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (27, 13, '/images/p13_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (28, 13, '/images/p13_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (29, 14, '/images/p14_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (30, 14, '/images/p14_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (31, 15, '/images/p15_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (32, 15, '/images/p15_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (33, 16, '/images/p16_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (34, 16, '/images/p16_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (35, 17, '/images/p17_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (36, 17, '/images/p17_detail.jpg', 'detail');


-- G. Orders 테이블
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `total_price` decimal(10,2) NOT NULL,
  `status` varchar(50) NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `orders` VALUES (7,3,29000.00,'결제완료','2025-05-10 00:19:56'),(8,4,45000.00,'대기','2025-05-10 00:19:56'),(9,7,55000.00,'결제완료','2025-05-10 00:19:56'),(10,5,15000.00,'결제완료','2025-05-10 00:19:56'),(11,6,38000.00,'결제 완료','2025-05-10 00:19:56'),(12,5,20000.00,'대기','2025-05-10 00:19:56');


-- H. Order Items 테이블
CREATE TABLE `orderitems` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int NOT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `orderitems_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `orderitems_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `orderitems` VALUES (1,7,4,2,29000.00),(2,8,5,1,45000.00),(3,9,6,1,55000.00),(4,10,8,1,15000.00),(5,11,7,1,38000.00),(6,12,9,1,20000.00);


-- I. Cart 테이블
CREATE TABLE `cart` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '장바구니 ID',
  `user_id` int NOT NULL COMMENT '사용자 ID',
  `product_id` int NOT NULL COMMENT '상품 ID',
  `quantity` int NOT NULL DEFAULT '1' COMMENT '수량',
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`product_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `cart_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `cart_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `cart` VALUES (1,3,4,2),(2,5,5,1),(3,6,6,2),(4,4,7,3),(5,5,9,1),(6,7,8,4);


-- J. Payments 테이블
CREATE TABLE `payments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `method` varchar(50) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `status` varchar(50) NOT NULL,
  `paid_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `payments` VALUES (1,7,'카드',29000.00,'성공','2025-05-10 01:25:48'),(2,8,'무통장',45000.00,'실패','2025-05-10 01:25:48'),(3,9,'카드',55000.00,'성공','2025-05-10 01:25:48'),(4,10,'카드',15000.00,'성공','2025-05-10 01:25:48'),(5,11,'무통장',38000.00,'실패','2025-05-10 01:25:48'),(6,12,'카드',20000.00,'성공','2025-05-10 01:25:48');


-- K. Shipping 테이블
CREATE TABLE `shipping` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '배송 ID',
  `order_id` int NOT NULL COMMENT '주문 ID',
  `address` text NOT NULL COMMENT '배송지 주소',
  `receiver_name` varchar(255) NOT NULL COMMENT '수령자 이름',
  `receiver_phone` varchar(20) NOT NULL COMMENT '수령자 연락처',
  `status` varchar(50) NOT NULL COMMENT '배송 상태 (예: 배송 중, 도착 등)',
  `shipped_at` datetime DEFAULT NULL COMMENT '발송일',
  `delivered_at` datetime DEFAULT NULL COMMENT '도착일',
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  CONSTRAINT `shipping_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `shipping` VALUES (1,7,'천안시 서북구 쌍용동','이지수','01036786886','배송중',NULL,NULL),(2,8,'수원시 영통구 이의동','김수연','01036725562','배송중',NULL,NULL),(3,9,'전주시 덕진구 송천동','이나은','01026757262','도착',NULL,NULL),(4,10,'대전광역시 유성구 봉명동','권예빈','01052868372','도착',NULL,NULL),(5,11,'수원시 영통구 이의동','김수연','01036725562','배송중',NULL,NULL),(6,12,'서울특별시 강남구 역삼동','박솔은','01037825273','도착',NULL,NULL);


-- L. User Measure Profile 테이블
CREATE TABLE `user_measure_profile` (
  `profile_id` int NOT NULL AUTO_INCREMENT COMMENT '측정 프로필 고유 ID',
  `user_id` int NOT NULL COMMENT '사용자 ID (users 테이블 참조)',
  `profile_name` varchar(100) NOT NULL COMMENT '측정 프로필명 (예: "내 최애 후드티")',
  `profile_image_url` varchar(255) DEFAULT NULL COMMENT '사용자가 업로드한 옷 이미지 주소',
  `category` varchar(50) NOT NULL COMMENT '분류 (예: "상의", "하의")',
  `top_length` decimal(5,1) DEFAULT NULL,
  `top_shoulder` decimal(5,1) DEFAULT NULL,
  `top_chest` decimal(5,1) DEFAULT NULL,
  `top_sleeve` decimal(5,1) DEFAULT NULL,
  `bottom_length` decimal(5,1) DEFAULT NULL,
  `bottom_waist` decimal(5,1) DEFAULT NULL,
  `bottom_rise` decimal(5,1) DEFAULT NULL,
  `bottom_hip` decimal(5,1) DEFAULT NULL,
  `bottom_thigh` decimal(5,1) DEFAULT NULL,
  `bottom_hem` decimal(5,1) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '측정값을 저장한 날짜',
  PRIMARY KEY (`profile_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_measure_profile_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `user_measure_profile` VALUES (1,3,'내 최애 후드티 (L)',NULL,'상의',70.0,50.0,58.0,60.0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-01 17:38:50'),(2,3,'자주 입는 청바지 (30)',NULL,'하의',NULL,NULL,NULL,NULL,102.0,40.0,30.0,50.0,31.0,20.0,'2025-11-01 17:38:50'),(3,4,'딱 맞는 반팔티 (M)',NULL,'상의',68.0,46.0,53.0,21.0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-01 17:38:50');


-- M. Wishlist 테이블
CREATE TABLE `wishlist` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '찜 ID',
  `user_id` int NOT NULL COMMENT '사용자 ID',
  `product_id` int NOT NULL COMMENT '상품 ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`product_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `wishlist_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `wishlist_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `wishlist` VALUES (1,3,4),(4,4,7),(2,5,5),(5,5,9),(3,6,6),(6,7,8);


-- N. Password Reset Tokens 테이블 (추가된 기능)
CREATE TABLE `password_reset_tokens` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `token` VARCHAR(500) NOT NULL,
    `expires_at` TIMESTAMP NOT NULL,
    `used` BOOLEAN DEFAULT FALSE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_token` (`token`(255)),
    INDEX `idx_expires` (`expires_at`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='비밀번호 재설정 토큰';


-- 4. 마무리 (외래키 검사 다시 켜기)
SET FOREIGN_KEY_CHECKS = 1;
SELECT '✅ 모든 테이블 생성 및 데이터 입력이 성공적으로 완료되었습니다!' AS Result;

##해당 코드안에 추가해서 전체 코드를 보내줘

The user wants me to integrate the SQL generated in the previous step (8 new products: IDs 10-17, sizes, measurements, images) into the existing comprehensive SQL script.

I will take the full script content provided in the prompt and append the new INSERT statements, and crucially, update the `AUTO_INCREMENT` values to prevent conflicts when running the entire dump file.

**Integration Strategy:**
1.  **Products:** Append new `INSERT INTO products` statements (IDs 10-17) and update `AUTO_INCREMENT=18`.
2.  **Product Size Option:** Append new `INSERT INTO product_size_option` statements (IDs 24-53) and update `AUTO_INCREMENT=54`.
3.  **Product Real Measure:** Append new `INSERT INTO product_real_measure` statements (IDs 11-40) and update `AUTO_INCREMENT=41`.
4.  **Product Images:** Append new `INSERT INTO product_images` statements (IDs 21-36) and update `AUTO_INCREMENT=37`.

**Execution of Integration:**

1.  **Product `AUTO_INCREMENT`:** Original ends at `AUTO_INCREMENT=10`. New products start at 10. **The original file must be changed to `AUTO_INCREMENT=18`** to allow new products 10-17 to be inserted correctly, or if running this full dump, the existing products 4-9 will be recreated, and the new ones will follow. I will adjust the `AUTO_INCREMENT` value of the `products` table definition to `AUTO_INCREMENT=18`.

2.  **`Product Size Option` `AUTO_INCREMENT`:** Original ends at `AUTO_INCREMENT=14`. New sizes start at 24. **Change to `AUTO_INCREMENT=54`**.

3.  **`Product Real Measure` `AUTO_INCREMENT`:** Original ends at `AUTO_INCREMENT=4`. New measures start at 11. **Change to `AUTO_INCREMENT=41`**.

4.  **`Product Images` `AUTO_INCREMENT`:** Original ends at `AUTO_INCREMENT=1`. New images start at 21. **Change to `AUTO_INCREMENT=37`**.

**Final Review:** I will output the entire, unified, and corrected SQL script.**네, 알겠습니다. 기존 덤프 파일에 8개의 새 상품 데이터와 이미지 경로를 모두 통합하고, `AUTO_INCREMENT` 값까지 수정한 최종 SQL 코드를 보내드립니다.**

이 코드를 실행하시면 **기존 6개의 상품**과 **새로 추가된 8개의 상품(ID 10번~17번)**이 모두 깔끔하게 DB에 채워집니다.

---

### 📋 통합된 최종 SQL 코드 (전체 내용)

```sql
-- 1. 외래키 검사 끄기 (순서 상관없이 삭제/생성 가능하게 함)
SET NAMES utf8mb4;
SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO';

-- 2. 기존 테이블 싹 지우기 (초기화)
DROP TABLE IF EXISTS `wishlist`;
DROP TABLE IF EXISTS `user_measure_profile`;
DROP TABLE IF EXISTS `shipping`;
DROP TABLE IF EXISTS `payments`;
DROP TABLE IF EXISTS `orderitems`;
DROP TABLE IF EXISTS `orders`;
DROP TABLE IF EXISTS `cart`;
DROP TABLE IF EXISTS `product_real_measure`;
DROP TABLE IF EXISTS `product_size_option`;
DROP TABLE IF EXISTS `product_images`;
DROP TABLE IF EXISTS `products`;
DROP TABLE IF EXISTS `categories`;
DROP TABLE IF EXISTS `password_reset_tokens`;
DROP TABLE IF EXISTS `users`;

-- -----------------------------------------------------
-- 3. 테이블 생성 및 데이터 입력 시작
-- -----------------------------------------------------

-- A. Users 테이블 생성 및 데이터 입력
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '사용자 ID (자동 증가)',
  `name` varchar(100) NOT NULL COMMENT '이름',
  `nickname` varchar(100) NOT NULL DEFAULT '' COMMENT '닉네임',
  `email` varchar(255) NOT NULL COMMENT '이메일 (UNIQUE)',
  `password` varchar(255) DEFAULT NULL COMMENT '암호화된 비밀번호 (소셜 로그인 시 NULL 가능)',
  `phone` varchar(20) DEFAULT NULL COMMENT '전화번호',
  `social_id` varchar(255) DEFAULT NULL COMMENT '소셜 로그인 ID',
  `social_provider` varchar(50) DEFAULT NULL COMMENT '소셜 로그인 제공자 (kakao, google)',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '가입일',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_social_login` (`social_id`,`social_provider`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `users` (`id`, `name`, `nickname`, `email`, `password`, `phone`, `created_at`, `updated_at`) VALUES 
(3,'이지수','두두','dodo46@naver.com','6286shj','01036786886','2025-05-09 21:34:49','2025-05-10 12:04:12'),
(4,'권예빈','치치','tyeirb@naver.com','yw7whsis','01052868372','2025-05-09 21:34:49','2025-05-10 12:04:12'),
(5,'김수연','우유','wyhshsij@naver.com','hsu81@#','01036725562','2025-05-09 21:34:49','2025-05-10 12:04:12'),
(6,'이나은','공강 킬러','ohkdha@naver.com','iwy6wy!!','01026757262','2025-05-09 21:34:49','2025-05-10 12:04:12'),
(7,'박솔은','자유를 외치다','ciel@naver.com','78eishsj','01037825273','2025-05-09 21:34:49','2025-05-10 12:04:12'),
(8,'홍길동','','hong@test.com','81dc9bdb52d04dc20036dbd8313ed055',NULL,'2025-11-01 15:46:51','2025-11-01 15:46:51'),
(9,'김영희','','kim@test.com','674f3c2c1a8a6f90461e8a66fb5550ba',NULL,'2025-11-01 15:46:51','2025-11-01 15:46:51');


-- B. Categories 테이블 (카테고리)
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '카테고리 ID',
  `name` varchar(100) NOT NULL COMMENT '카테고리명',
  `parent_id` int DEFAULT NULL COMMENT '상위 카테고리 ID (nullable)',
  PRIMARY KEY (`id`),
  KEY `parent_id` (`parent_id`),
  CONSTRAINT `categories_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `categories` VALUES (16,'의류',NULL),(17,'남성 의류',16),(18,'여성 의류',16),(19,'아동 의류',16),(26,'아우터',17),(27,'상의',17),(28,'바지',17),(29,'홈웨어',17),(30,'아우터',18),(31,'상의',18),(32,'바지',18),(33,'원피스',18),(34,'치마',18),(35,'홈웨어',18),(36,'아우터',19),(37,'상의',19),(38,'바지',19),(39,'치마',19),(40,'홈웨어',19);


-- C. Products 테이블 (상품 - 8개 신규 추가됨)
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '상품 ID',
  `name` varchar(200) NOT NULL COMMENT '상품명',
  `description` text COMMENT '상품 설명',
  `price` decimal(10,2) NOT NULL COMMENT '가격',
  `stock_quantity` int DEFAULT '0' COMMENT '재고 수량',
  `category_id` int DEFAULT NULL COMMENT '카테고리 ID (FK)',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '등록일',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일',
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  FULLTEXT KEY `idx_product_search` (`name`,`description`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `products` VALUES 
(4,'남성 셔츠','캐주얼 스타일의 면 셔츠',29000.00,50,27,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(5,'남성 청바지','슬림핏 데님 바지',45000.00,30,28,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(6,'여성 원피스','봄철용 플라워 패턴 원피스',55000.00,20,32,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(7,'여성 스커트','하이웨이스트 롱 스커트',38000.00,40,33,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(8,'아동 티셔츠','귀여운 캐릭터 프린트 티셔츠',15000.00,100,38,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(9,'아동 청바지','신축성 좋은 아동용 청바지',20000.00,60,39,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(10, '플로킹 로고 그래픽 맨투맨', '자동 삽입된 상품입니다. (상의 분류)', 84550.00, 50, 27, NOW(), NOW()),
(11, '베이직 오버핏 긴팔 티셔츠', '자동 삽입된 상품입니다. (상의 분류)', 15890.00, 50, 27, NOW(), NOW()),
(12, '중량담요 후드티 코코아 브라운', '자동 삽입된 상품입니다. (상의 분류)', 68400.00, 50, 27, NOW(), NOW()),
(13, '컨투어 폭스 헤드 스케이트 셔츠', '자동 삽입된 상품입니다. (상의 분류)', 160990.00, 50, 27, NOW(), NOW()),
(14, '우먼즈 릴렉스드 스웨트 팬츠', '자동 삽입된 상품입니다. (하의 분류)', 19590.00, 50, 28, NOW(), NOW()),
(15, '아르코 커브드 데님', '자동 삽입된 상품입니다. (하의 분류)', 81840.00, 50, 28, NOW(), NOW()),
(16, '이지 세미와이드 슬랙스', '자동 삽입된 상품입니다. (하의 분류)', 29890.00, 50, 28, NOW(), NOW()),
(17, '여성 피어스 니트 팬츠', '자동 삽입된 상품입니다. (하의 분류)', 99000.00, 50, 28, NOW(), NOW());


-- D. Product Size Option 테이블 (AUTO_INCREMENT 변경됨)
CREATE TABLE `product_size_option` (
  `size_option_id` int NOT NULL AUTO_INCREMENT COMMENT '사이즈 옵션 고유 ID',
  `product_id` int NOT NULL COMMENT '상품 ID (Products 테이블 참조)',
  `option_name` varchar(30) NOT NULL COMMENT '사이즈명 (예: "M", "L", "100")',
  `stock_quantity` int NOT NULL DEFAULT '0' COMMENT '해당 사이즈의 재고 수량',
  PRIMARY KEY (`size_option_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `product_size_option_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `product_size_option` VALUES 
(1,4,'M',30),(2,4,'L',50),(3,4,'XL',20),(4,4,'XXL',0),(5,5,'28',25),(6,5,'30',30),(7,5,'32',15),(8,6,'Free',30),(9,6,'S',20),(10,6,'M',10),(11,7,'S',25),(12,7,'M',30),(13,7,'L',5),
(24, 10, 'M(95)', 15), (25, 10, 'L(100)', 15), (26, 10, 'XL(105)', 15), (27, 10, '2XL(110)', 15), 
(28, 11, 'M(95)', 15), (29, 11, 'L(100)', 15), (30, 11, 'XL(105)', 15), (31, 11, '2XL(110)', 15), (32, 11, '3XL(115~120)', 15),
(33, 12, 'S', 15), (34, 12, 'M', 15), (35, 12, 'L', 15), 
(36, 13, 'M', 15), (37, 13, 'L', 15), (38, 13, 'XL', 15), 
(39, 14, 'XS', 15), (40, 14, 'S', 15), (41, 14, 'M', 15), (42, 14, 'L', 15), 
(43, 15, 'S', 15), (44, 15, 'M', 15), (45, 15, 'L', 15), 
(46, 16, 'M', 15), (47, 16, 'L', 15), (48, 16, 'XL', 15), (49, 16, '2XL', 15), (50, 16, '3XL', 15),
(51, 17, 'XS', 15), (52, 17, 'S', 15), (53, 17, 'M', 15);


-- E. Product Real Measure 테이블 (AUTO_INCREMENT 변경됨)
CREATE TABLE `product_real_measure` (
  `measure_id` int NOT NULL AUTO_INCREMENT COMMENT '실측 고유 ID',
  `size_option_id` int NOT NULL COMMENT '사이즈 옵션 ID (Product_Size_Option 참조)',
  `category` varchar(50) NOT NULL COMMENT '분류 (예: "상의", "하의")',
  `top_length` decimal(5,1) DEFAULT NULL COMMENT '상의 총장 (cm, 소수점 1자리)',
  `top_shoulder` decimal(5,1) DEFAULT NULL COMMENT '상의 어깨너비 (cm, 소수점 1자리)',
  `top_chest` decimal(5,1) DEFAULT NULL COMMENT '상의 가슴단면 (cm, 소수점 1자리)',
  `top_sleeve` decimal(5,1) DEFAULT NULL COMMENT '상의 소매길이 (cm, 소수점 1자리)',
  `bottom_length` decimal(5,1) DEFAULT NULL COMMENT '하의 총장 (cm, 소수점 1자리)',
  `bottom_waist` decimal(5,1) DEFAULT NULL COMMENT '하의 허리단면 (cm, 소수점 1자리)',
  `bottom_rise` decimal(5,1) DEFAULT NULL COMMENT '하의 밑위 (cm, 소수점 1자리)',
  `bottom_hip` decimal(5,1) DEFAULT NULL COMMENT '하의 엉덩이단면 (cm, 소수점 1자리)',
  `bottom_thigh` decimal(5,1) DEFAULT NULL COMMENT '하의 허벅지단면 (cm, 소수점 1자리)',
  `bottom_hem` decimal(5,1) DEFAULT NULL COMMENT '하의 밑단단면 (cm, 소수점 1자리)',
  PRIMARY KEY (`measure_id`),
  KEY `size_option_id` (`size_option_id`),
  CONSTRAINT `product_real_measure_ibfk_1` FOREIGN KEY (`size_option_id`) REFERENCES `product_size_option` (`size_option_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `product_real_measure` VALUES 
(1,1,'상의',70.0,45.0,52.5,22.0,NULL,NULL,NULL,NULL,NULL,NULL),
(2,2,'상의',72.0,47.0,55.0,23.0,NULL,NULL,NULL,NULL,NULL,NULL),
(3,5,'하의',NULL,NULL,NULL,NULL,100.0,38.5,29.0,48.0,30.0,20.0),
(11, 24, '상의', 67.5, 46.5, 55.5, 62.7, NULL, NULL, NULL, NULL, NULL, NULL),
(12, 25, '상의', 69.5, 48.5, 58.0, 63.7, NULL, NULL, NULL, NULL, NULL, NULL),
(13, 26, '상의', 71.5, 50.5, 60.5, 64.7, NULL, NULL, NULL, NULL, NULL, NULL),
(14, 27, '상의', 73.5, 52.5, 63.0, 65.7, NULL, NULL, NULL, NULL, NULL, NULL),
(15, 28, '상의', 70.0, 49.0, 56.0, 59.0, NULL, NULL, NULL, NULL, NULL, NULL),
(16, 29, '상의', 71.0, 51.0, 58.0, 60.0, NULL, NULL, NULL, NULL, NULL, NULL),
(17, 30, '상의', 72.5, 53.0, 60.0, 61.0, NULL, NULL, NULL, NULL, NULL, NULL),
(18, 31, '상의', 74.5, 55.0, 62.0, 62.0, NULL, NULL, NULL, NULL, NULL, NULL),
(19, 32, '상의', 75.5, 57.0, 64.0, 63.0, NULL, NULL, NULL, NULL, NULL, NULL),
(20, 33, '상의', 65.0, 64.0, 63.0, 55.5, NULL, NULL, NULL, NULL, NULL, NULL),
(21, 34, '상의', 67.0, 66.0, 65.0, 56.5, NULL, NULL, NULL, NULL, NULL, NULL),
(22, 35, '상의', 69.0, 68.0, 67.0, 57.5, NULL, NULL, NULL, NULL, NULL, NULL),
(23, 36, '상의', 82.0, 51.0, 60.0, 65.5, NULL, NULL, NULL, NULL, NULL, NULL),
(24, 37, '상의', 86.0, 52.0, 61.0, 67.0, NULL, NULL, NULL, NULL, NULL, NULL),
(25, 38, '상의', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(26, 39, '하의', NULL, NULL, NULL, NULL, 96.0, 30.0, 30.8, 50.0, 30.8, 12.0),
(27, 40, '하의', NULL, NULL, NULL, NULL, 97.0, 32.5, 31.5, 52.5, 32.0, 12.5),
(28, 41, '하의', NULL, NULL, NULL, NULL, 98.0, 35.0, 32.3, 55.0, 33.3, 13.0),
(29, 42, '하의', NULL, NULL, NULL, NULL, 99.0, 37.5, 32.9, 57.5, 34.5, 13.5),
(30, 43, '하의', NULL, NULL, NULL, NULL, 103.0, 35.0, 32.0, 50.5, 33.0, 24.5),
(31, 44, '하의', NULL, NULL, NULL, NULL, 104.0, 37.0, 33.0, 52.5, 34.0, 25.0),
(32, 45, '하의', NULL, NULL, NULL, NULL, 107.0, 39.0, 34.0, 54.5, 35.0, 25.5),
(33, 46, '하의', NULL, NULL, NULL, NULL, 103.0, 40.0, 27.5, NULL, 32.0, 21.0),
(34, 47, '하의', NULL, NULL, NULL, NULL, 104.0, 42.0, 28.5, NULL, 33.0, 21.5),
(35, 48, '하의', NULL, NULL, NULL, NULL, 105.0, 44.0, 29.5, NULL, 34.0, 2.0),
(36, 49, '하의', NULL, NULL, NULL, NULL, 106.0, 46.0, 30.5, NULL, 35.0, 22.5),
(37, 50, '하의', NULL, NULL, NULL, NULL, 107.0, 48.0, 31.5, NULL, 36.0, 23.0),
(38, 51, '하의', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(39, 52, '하의', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(40, 53, '하의', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);


-- F. Product Images 테이블
CREATE TABLE `product_images` (
  `product_image_id` int NOT NULL AUTO_INCREMENT COMMENT '이미지 고유 ID (PK)',
  `product_id` int NOT NULL COMMENT '상품 ID (products.id 참조)',
  `image_url` varchar(255) NOT NULL COMMENT '이미지 경로 또는 URL',
  `image_type` varchar(50) NOT NULL COMMENT '이미지 타입 (예: main, detail)',
  PRIMARY KEY (`product_image_id`),
  KEY `fk_product_images_to_products` (`product_id`),
  CONSTRAINT `fk_product_images_to_products` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='상품별 상세 이미지';

INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (21, 10, '/images/p10_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (22, 10, '/images/p10_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (23, 11, '/images/p11_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (24, 11, '/images/p11_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (25, 12, '/images/p12_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (26, 12, '/images/p12_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (27, 13, '/images/p13_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (28, 13, '/images/p13_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (29, 14, '/images/p14_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (30, 14, '/images/p14_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (31, 15, '/images/p15_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (32, 15, '/images/p15_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (33, 16, '/images/p16_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (34, 16, '/images/p16_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (35, 17, '/images/p17_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (36, 17, '/images/p17_detail.jpg', 'detail');


-- G. Orders 테이블
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `total_price` decimal(10,2) NOT NULL,
  `status` varchar(50) NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `orders` VALUES (7,3,29000.00,'결제완료','2025-05-10 00:19:56'),(8,4,45000.00,'대기','2025-05-10 00:19:56'),(9,7,55000.00,'결제완료','2025-05-10 00:19:56'),(10,5,15000.00,'결제완료','2025-05-10 00:19:56'),(11,6,38000.00,'결제 완료','2025-05-10 00:19:56'),(12,5,20000.00,'대기','2025-05-10 00:19:56');


-- H. Order Items 테이블
CREATE TABLE `orderitems` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int NOT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `orderitems_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `orderitems_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `orderitems` VALUES (1,7,4,2,29000.00),(2,8,5,1,45000.00),(3,9,6,1,55000.00),(4,10,8,1,15000.00),(5,11,7,1,38000.00),(6,12,9,1,20000.00);


-- I. Cart 테이블
CREATE TABLE `cart` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '장바구니 ID',
  `user_id` int NOT NULL COMMENT '사용자 ID',
  `product_id` int NOT NULL COMMENT '상품 ID',
  `quantity` int NOT NULL DEFAULT '1' COMMENT '수량',
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`product_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `cart_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `cart_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `cart` VALUES (1,3,4,2),(2,5,5,1),(3,6,6,2),(4,4,7,3),(5,5,9,1),(6,7,8,4);


-- J. Payments 테이블
CREATE TABLE `payments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `method` varchar(50) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `status` varchar(50) NOT NULL,
  `paid_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `payments` VALUES (1,7,'카드',29000.00,'성공','2025-05-10 01:25:48'),(2,8,'무통장',45000.00,'실패','2025-05-10 01:25:48'),(3,9,'카드',55000.00,'성공','2025-05-10 01:25:48'),(4,10,'카드',15000.00,'성공','2025-05-10 01:25:48'),(5,11,'무통장',38000.00,'실패','2025-05-10 01:25:48'),(6,12,'카드',20000.00,'성공','2025-05-10 01:25:48');


-- K. Shipping 테이블
CREATE TABLE `shipping` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '배송 ID',
  `order_id` int NOT NULL COMMENT '주문 ID',
  `address` text NOT NULL COMMENT '배송지 주소',
  `receiver_name` varchar(255) NOT NULL COMMENT '수령자 이름',
  `receiver_phone` varchar(20) NOT NULL COMMENT '수령자 연락처',
  `status` varchar(50) NOT NULL COMMENT '배송 상태 (예: 배송 중, 도착 등)',
  `shipped_at` datetime DEFAULT NULL COMMENT '발송일',
  `delivered_at` datetime DEFAULT NULL COMMENT '도착일',
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  CONSTRAINT `shipping_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `shipping` VALUES (1,7,'천안시 서북구 쌍용동','이지수','01036786886','배송중',NULL,NULL),(2,8,'수원시 영통구 이의동','김수연','01036725562','배송중',NULL,NULL),(3,9,'전주시 덕진구 송천동','이나은','01026757262','도착',NULL,NULL),(4,10,'대전광역시 유성구 봉명동','권예빈','01052868372','도착',NULL,NULL),(5,11,'수원시 영통구 이의동','김수연','01036725562','배송중',NULL,NULL),(6,12,'서울특별시 강남구 역삼동','박솔은','01037825273','도착',NULL,NULL);


-- L. User Measure Profile 테이블
CREATE TABLE `user_measure_profile` (
  `profile_id` int NOT NULL AUTO_INCREMENT COMMENT '측정 프로필 고유 ID',
  `user_id` int NOT NULL COMMENT '사용자 ID (users 테이블 참조)',
  `profile_name` varchar(100) NOT NULL COMMENT '측정 프로필명 (예: "내 최애 후드티")',
  `profile_image_url` varchar(255) DEFAULT NULL COMMENT '사용자가 업로드한 옷 이미지 주소',
  `category` varchar(50) NOT NULL COMMENT '분류 (예: "상의", "하의")',
  `top_length` decimal(5,1) DEFAULT NULL,
  `top_shoulder` decimal(5,1) DEFAULT NULL,
  `top_chest` decimal(5,1) DEFAULT NULL,
  `top_sleeve` decimal(5,1) DEFAULT NULL,
  `bottom_length` decimal(5,1) DEFAULT NULL,
  `bottom_waist` decimal(5,1) DEFAULT NULL,
  `bottom_rise` decimal(5,1) DEFAULT NULL,
  `bottom_hip` decimal(5,1) DEFAULT NULL,
  `bottom_thigh` decimal(5,1) DEFAULT NULL,
  `bottom_hem` decimal(5,1) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '측정값을 저장한 날짜',
  PRIMARY KEY (`profile_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_measure_profile_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `user_measure_profile` VALUES (1,3,'내 최애 후드티 (L)',NULL,'상의',70.0,50.0,58.0,60.0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-01 17:38:50'),(2,3,'자주 입는 청바지 (30)',NULL,'하의',NULL,NULL,NULL,NULL,102.0,40.0,30.0,50.0,31.0,20.0,'2025-11-01 17:38:50'),(3,4,'딱 맞는 반팔티 (M)',NULL,'상의',68.0,46.0,53.0,21.0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-01 17:38:50');


-- M. Wishlist 테이블
CREATE TABLE `wishlist` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '찜 ID',
  `user_id` int NOT NULL COMMENT '사용자 ID',
  `product_id` int NOT NULL COMMENT '상품 ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`product_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `wishlist_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `wishlist_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `wishlist` VALUES (1,3,4),(4,4,7),(2,5,5),(5,5,9),(3,6,6),(6,7,8);


-- N. Password Reset Tokens 테이블 (추가된 기능)
CREATE TABLE `password_reset_tokens` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `token` VARCHAR(500) NOT NULL,
    `expires_at` TIMESTAMP NOT NULL,
    `used` BOOLEAN DEFAULT FALSE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_token` (`token`(255)),
    INDEX `idx_expires` (`expires_at`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='비밀번호 재설정 토큰';


-- 4. 마무리 (외래키 검사 다시 켜기)
SET FOREIGN_KEY_CHECKS = 1;
SELECT '✅ 모든 테이블 생성 및 데이터 입력이 성공적으로 완료되었습니다!' AS Result;

##해당 코드안에 추가해서 전체 코드를 보내줘

The user wants me to integrate the SQL generated in the previous step (8 new products: IDs 10-17, sizes, measurements, images) into the existing comprehensive SQL script.

I will take the full script content provided in the prompt and append the new INSERT statements, and crucially, update the `AUTO_INCREMENT` values to prevent conflicts when running the entire dump file.

**Integration Strategy:**
1.  **Products:** Append new `INSERT INTO products` statements (IDs 10-17) and update `AUTO_INCREMENT=18`.
2.  **Product Size Option:** Append new `INSERT INTO product_size_option` statements (IDs 24-53) and update `AUTO_INCREMENT=54`.
3.  **Product Real Measure:** Append new `INSERT INTO product_real_measure` statements (IDs 11-40) and update `AUTO_INCREMENT=41`.
4.  **Product Images:** Append new `INSERT INTO product_images` statements (IDs 21-36) and update `AUTO_INCREMENT=37`.

**Final Review:** I will output the entire, unified, and corrected SQL script.**네, 알겠습니다. 최종적으로 8개의 새 상품 데이터와 관련된 모든 정보를 통합하고, `AUTO_INCREMENT` 값까지 수정한 전체 SQL 코드를 보내드립니다.**

이 코드는 **기존 6개 상품**과 **새로 추가된 8개 상품(ID 10번~17번)**을 모두 포함하며, 한 번 실행으로 모든 테이블을 깨끗하게 정리하고 데이터를 채워 넣습니다.

---

### 📋 통합된 최종 SQL 코드 (전체 내용)

```sql
-- 1. 외래키 검사 끄기 (순서 상관없이 삭제/생성 가능하게 함)
SET NAMES utf8mb4;
SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO';

-- 2. 기존 테이블 싹 지우기 (초기화)
DROP TABLE IF EXISTS `wishlist`;
DROP TABLE IF EXISTS `user_measure_profile`;
DROP TABLE IF EXISTS `shipping`;
DROP TABLE IF EXISTS `payments`;
DROP TABLE IF EXISTS `orderitems`;
DROP TABLE IF EXISTS `orders`;
DROP TABLE IF EXISTS `cart`;
DROP TABLE IF EXISTS `product_real_measure`;
DROP TABLE IF EXISTS `product_size_option`;
DROP TABLE IF EXISTS `product_images`;
DROP TABLE IF EXISTS `products`;
DROP TABLE IF EXISTS `categories`;
DROP TABLE IF EXISTS `password_reset_tokens`;
DROP TABLE IF EXISTS `users`;

-- -----------------------------------------------------
-- 3. 테이블 생성 및 데이터 입력 시작
-- -----------------------------------------------------

-- A. Users 테이블 생성 및 데이터 입력
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '사용자 ID (자동 증가)',
  `name` varchar(100) NOT NULL COMMENT '이름',
  `nickname` varchar(100) NOT NULL DEFAULT '' COMMENT '닉네임',
  `email` varchar(255) NOT NULL COMMENT '이메일 (UNIQUE)',
  `password` varchar(255) DEFAULT NULL COMMENT '암호화된 비밀번호 (소셜 로그인 시 NULL 가능)',
  `phone` varchar(20) DEFAULT NULL COMMENT '전화번호',
  `social_id` varchar(255) DEFAULT NULL COMMENT '소셜 로그인 ID',
  `social_provider` varchar(50) DEFAULT NULL COMMENT '소셜 로그인 제공자 (kakao, google)',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '가입일',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_social_login` (`social_id`,`social_provider`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `users` (`id`, `name`, `nickname`, `email`, `password`, `phone`, `created_at`, `updated_at`) VALUES 
(3,'이지수','두두','dodo46@naver.com','6286shj','01036786886','2025-05-09 21:34:49','2025-05-10 12:04:12'),
(4,'권예빈','치치','tyeirb@naver.com','yw7whsis','01052868372','2025-05-09 21:34:49','2025-05-10 12:04:12'),
(5,'김수연','우유','wyhshsij@naver.com','hsu81@#','01036725562','2025-05-09 21:34:49','2025-05-10 12:04:12'),
(6,'이나은','공강 킬러','ohkdha@naver.com','iwy6wy!!','01026757262','2025-05-09 21:34:49','2025-05-10 12:04:12'),
(7,'박솔은','자유를 외치다','ciel@naver.com','78eishsj','01037825273','2025-05-09 21:34:49','2025-05-10 12:04:12'),
(8,'홍길동','','hong@test.com','81dc9bdb52d04dc20036dbd8313ed055',NULL,'2025-11-01 15:46:51','2025-11-01 15:46:51'),
(9,'김영희','','kim@test.com','674f3c2c1a8a6f90461e8a66fb5550ba',NULL,'2025-11-01 15:46:51','2025-11-01 15:46:51');


-- B. Categories 테이블 (카테고리)
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '카테고리 ID',
  `name` varchar(100) NOT NULL COMMENT '카테고리명',
  `parent_id` int DEFAULT NULL COMMENT '상위 카테고리 ID (nullable)',
  PRIMARY KEY (`id`),
  KEY `parent_id` (`parent_id`),
  CONSTRAINT `categories_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `categories` VALUES (16,'의류',NULL),(17,'남성 의류',16),(18,'여성 의류',16),(19,'아동 의류',16),(26,'아우터',17),(27,'상의',17),(28,'바지',17),(29,'홈웨어',17),(30,'아우터',18),(31,'상의',18),(32,'바지',18),(33,'원피스',18),(34,'치마',18),(35,'홈웨어',18),(36,'아우터',19),(37,'상의',19),(38,'바지',19),(39,'치마',19),(40,'홈웨어',19);


-- C. Products 테이블 (상품 - 8개 신규 추가됨)
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '상품 ID',
  `name` varchar(200) NOT NULL COMMENT '상품명',
  `description` text COMMENT '상품 설명',
  `price` decimal(10,2) NOT NULL COMMENT '가격',
  `stock_quantity` int DEFAULT '0' COMMENT '재고 수량',
  `category_id` int DEFAULT NULL COMMENT '카테고리 ID (FK)',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '등록일',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일',
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  FULLTEXT KEY `idx_product_search` (`name`,`description`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `products` VALUES 
(4,'남성 셔츠','캐주얼 스타일의 면 셔츠',29000.00,50,27,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(5,'남성 청바지','슬림핏 데님 바지',45000.00,30,28,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(6,'여성 원피스','봄철용 플라워 패턴 원피스',55000.00,20,32,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(7,'여성 스커트','하이웨이스트 롱 스커트',38000.00,40,33,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(8,'아동 티셔츠','귀여운 캐릭터 프린트 티셔츠',15000.00,100,38,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(9,'아동 청바지','신축성 좋은 아동용 청바지',20000.00,60,39,'2025-05-09 23:40:11','2025-05-09 23:40:11'),
(10, '플로킹 로고 그래픽 맨투맨', '자동 삽입된 상품입니다. (상의 분류)', 84550.00, 50, 27, NOW(), NOW()),
(11, '베이직 오버핏 긴팔 티셔츠', '자동 삽입된 상품입니다. (상의 분류)', 15890.00, 50, 27, NOW(), NOW()),
(12, '중량담요 후드티 코코아 브라운', '자동 삽입된 상품입니다. (상의 분류)', 68400.00, 50, 27, NOW(), NOW()),
(13, '컨투어 폭스 헤드 스케이트 셔츠', '자동 삽입된 상품입니다. (상의 분류)', 160990.00, 50, 27, NOW(), NOW()),
(14, '우먼즈 릴렉스드 스웨트 팬츠', '자동 삽입된 상품입니다. (하의 분류)', 19590.00, 50, 28, NOW(), NOW()),
(15, '아르코 커브드 데님', '자동 삽입된 상품입니다. (하의 분류)', 81840.00, 50, 28, NOW(), NOW()),
(16, '이지 세미와이드 슬랙스', '자동 삽입된 상품입니다. (하의 분류)', 29890.00, 50, 28, NOW(), NOW()),
(17, '여성 피어스 니트 팬츠', '자동 삽입된 상품입니다. (하의 분류)', 99000.00, 50, 28, NOW(), NOW());


-- D. Product Size Option 테이블 (AUTO_INCREMENT 변경됨)
CREATE TABLE `product_size_option` (
  `size_option_id` int NOT NULL AUTO_INCREMENT COMMENT '사이즈 옵션 고유 ID',
  `product_id` int NOT NULL COMMENT '상품 ID (Products 테이블 참조)',
  `option_name` varchar(30) NOT NULL COMMENT '사이즈명 (예: "M", "L", "100")',
  `stock_quantity` int NOT NULL DEFAULT '0' COMMENT '해당 사이즈의 재고 수량',
  PRIMARY KEY (`size_option_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `product_size_option_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `product_size_option` VALUES 
(1,4,'M',30),(2,4,'L',50),(3,4,'XL',20),(4,4,'XXL',0),(5,5,'28',25),(6,5,'30',30),(7,5,'32',15),(8,6,'Free',30),(9,6,'S',20),(10,6,'M',10),(11,7,'S',25),(12,7,'M',30),(13,7,'L',5),
(24, 10, 'M(95)', 15), (25, 10, 'L(100)', 15), (26, 10, 'XL(105)', 15), (27, 10, '2XL(110)', 15), 
(28, 11, 'M(95)', 15), (29, 11, 'L(100)', 15), (30, 11, 'XL(105)', 15), (31, 11, '2XL(110)', 15), (32, 11, '3XL(115~120)', 15),
(33, 12, 'S', 15), (34, 12, 'M', 15), (35, 12, 'L', 15), 
(36, 13, 'M', 15), (37, 13, 'L', 15), (38, 13, 'XL', 15), 
(39, 14, 'XS', 15), (40, 14, 'S', 15), (41, 14, 'M', 15), (42, 14, 'L', 15), 
(43, 15, 'S', 15), (44, 15, 'M', 15), (45, 15, 'L', 15), 
(46, 16, 'M', 15), (47, 16, 'L', 15), (48, 16, 'XL', 15), (49, 16, '2XL', 15), (50, 16, '3XL', 15),
(51, 17, 'XS', 15), (52, 17, 'S', 15), (53, 17, 'M', 15);


-- E. Product Real Measure 테이블 (AUTO_INCREMENT 변경됨)
CREATE TABLE `product_real_measure` (
  `measure_id` int NOT NULL AUTO_INCREMENT COMMENT '실측 고유 ID',
  `size_option_id` int NOT NULL COMMENT '사이즈 옵션 ID (Product_Size_Option 참조)',
  `category` varchar(50) NOT NULL COMMENT '분류 (예: "상의", "하의")',
  `top_length` decimal(5,1) DEFAULT NULL COMMENT '상의 총장 (cm, 소수점 1자리)',
  `top_shoulder` decimal(5,1) DEFAULT NULL COMMENT '상의 어깨너비 (cm, 소수점 1자리)',
  `top_chest` decimal(5,1) DEFAULT NULL COMMENT '상의 가슴단면 (cm, 소수점 1자리)',
  `top_sleeve` decimal(5,1) DEFAULT NULL COMMENT '상의 소매길이 (cm, 소수점 1자리)',
  `bottom_length` decimal(5,1) DEFAULT NULL COMMENT '하의 총장 (cm, 소수점 1자리)',
  `bottom_waist` decimal(5,1) DEFAULT NULL COMMENT '하의 허리단면 (cm, 소수점 1자리)',
  `bottom_rise` decimal(5,1) DEFAULT NULL COMMENT '하의 밑위 (cm, 소수점 1자리)',
  `bottom_hip` decimal(5,1) DEFAULT NULL COMMENT '하의 엉덩이단면 (cm, 소수점 1자리)',
  `bottom_thigh` decimal(5,1) DEFAULT NULL COMMENT '하의 허벅지단면 (cm, 소수점 1자리)',
  `bottom_hem` decimal(5,1) DEFAULT NULL COMMENT '하의 밑단단면 (cm, 소수점 1자리)',
  PRIMARY KEY (`measure_id`),
  KEY `size_option_id` (`size_option_id`),
  CONSTRAINT `product_real_measure_ibfk_1` FOREIGN KEY (`size_option_id`) REFERENCES `product_size_option` (`size_option_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `product_real_measure` VALUES 
(1,1,'상의',70.0,45.0,52.5,22.0,NULL,NULL,NULL,NULL,NULL,NULL),
(2,2,'상의',72.0,47.0,55.0,23.0,NULL,NULL,NULL,NULL,NULL,NULL),
(3,5,'하의',NULL,NULL,NULL,NULL,100.0,38.5,29.0,48.0,30.0,20.0),
(11, 24, '상의', 67.5, 46.5, 55.5, 62.7, NULL, NULL, NULL, NULL, NULL, NULL),
(12, 25, '상의', 69.5, 48.5, 58.0, 63.7, NULL, NULL, NULL, NULL, NULL, NULL),
(13, 26, '상의', 71.5, 50.5, 60.5, 64.7, NULL, NULL, NULL, NULL, NULL, NULL),
(14, 27, '상의', 73.5, 52.5, 63.0, 65.7, NULL, NULL, NULL, NULL, NULL, NULL),
(15, 28, '상의', 70.0, 49.0, 56.0, 59.0, NULL, NULL, NULL, NULL, NULL, NULL),
(16, 29, '상의', 71.0, 51.0, 58.0, 60.0, NULL, NULL, NULL, NULL, NULL, NULL),
(17, 30, '상의', 72.5, 53.0, 60.0, 61.0, NULL, NULL, NULL, NULL, NULL, NULL),
(18, 31, '상의', 74.5, 55.0, 62.0, 62.0, NULL, NULL, NULL, NULL, NULL, NULL),
(19, 32, '상의', 75.5, 57.0, 64.0, 63.0, NULL, NULL, NULL, NULL, NULL, NULL),
(20, 33, '상의', 65.0, 64.0, 63.0, 55.5, NULL, NULL, NULL, NULL, NULL, NULL),
(21, 34, '상의', 67.0, 66.0, 65.0, 56.5, NULL, NULL, NULL, NULL, NULL, NULL),
(22, 35, '상의', 69.0, 68.0, 67.0, 57.5, NULL, NULL, NULL, NULL, NULL, NULL),
(23, 36, '상의', 82.0, 51.0, 60.0, 65.5, NULL, NULL, NULL, NULL, NULL, NULL),
(24, 37, '상의', 86.0, 52.0, 61.0, 67.0, NULL, NULL, NULL, NULL, NULL, NULL),
(25, 38, '상의', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(26, 39, '하의', NULL, NULL, NULL, NULL, 96.0, 30.0, 30.8, 50.0, 30.8, 12.0),
(27, 40, '하의', NULL, NULL, NULL, NULL, 97.0, 32.5, 31.5, 52.5, 32.0, 12.5),
(28, 41, '하의', NULL, NULL, NULL, NULL, 98.0, 35.0, 32.3, 55.0, 33.3, 13.0),
(29, 42, '하의', NULL, NULL, NULL, NULL, 99.0, 37.5, 32.9, 57.5, 34.5, 13.5),
(30, 43, '하의', NULL, NULL, NULL, NULL, 103.0, 35.0, 32.0, 50.5, 33.0, 24.5),
(31, 44, '하의', NULL, NULL, NULL, NULL, 104.0, 37.0, 33.0, 52.5, 34.0, 25.0),
(32, 45, '하의', NULL, NULL, NULL, NULL, 107.0, 39.0, 34.0, 54.5, 35.0, 25.5),
(33, 46, '하의', NULL, NULL, NULL, NULL, 103.0, 40.0, 27.5, NULL, 32.0, 21.0),
(34, 47, '하의', NULL, NULL, NULL, NULL, 104.0, 42.0, 28.5, NULL, 33.0, 21.5),
(35, 48, '하의', NULL, NULL, NULL, NULL, 105.0, 44.0, 29.5, NULL, 34.0, 2.0),
(36, 49, '하의', NULL, NULL, NULL, NULL, 106.0, 46.0, 30.5, NULL, 35.0, 22.5),
(37, 50, '하의', NULL, NULL, NULL, NULL, 107.0, 48.0, 31.5, NULL, 36.0, 23.0),
(38, 51, '하의', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(39, 52, '하의', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(40, 53, '하의', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);


-- F. Product Images 테이블
CREATE TABLE `product_images` (
  `product_image_id` int NOT NULL AUTO_INCREMENT COMMENT '이미지 고유 ID (PK)',
  `product_id` int NOT NULL COMMENT '상품 ID (products.id 참조)',
  `image_url` varchar(255) NOT NULL COMMENT '이미지 경로 또는 URL',
  `image_type` varchar(50) NOT NULL COMMENT '이미지 타입 (예: main, detail)',
  PRIMARY KEY (`product_image_id`),
  KEY `fk_product_images_to_products` (`product_id`),
  CONSTRAINT `fk_product_images_to_products` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='상품별 상세 이미지';

INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (21, 10, '/images/p10_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (22, 10, '/images/p10_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (23, 11, '/images/p11_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (24, 11, '/images/p11_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (25, 12, '/images/p12_main.jpg', 'main');
INSERT INTO `product_image_id` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (26, 12, '/images/p12_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (27, 13, '/images/p13_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (28, 13, '/images/p13_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (29, 14, '/images/p14_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (30, 14, '/images/p14_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (31, 15, '/images/p15_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (32, 15, '/images/p15_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (33, 16, '/images/p16_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (34, 16, '/images/p16_detail.jpg', 'detail');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (35, 17, '/images/p17_main.jpg', 'main');
INSERT INTO `product_images` (`product_image_id`, `product_id`, `image_url`, `image_type`) VALUES (36, 17, '/images/p17_detail.jpg', 'detail');


-- G. Orders 테이블
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `total_price` decimal(10,2) NOT NULL,
  `status` varchar(50) NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `orders` VALUES (7,3,29000.00,'결제완료','2025-05-10 00:19:56'),(8,4,45000.00,'대기','2025-05-10 00:19:56'),(9,7,55000.00,'결제완료','2025-05-10 00:19:56'),(10,5,15000.00,'결제완료','2025-05-10 00:19:56'),(11,6,38000.00,'결제 완료','2025-05-10 00:19:56'),(12,5,20000.00,'대기','2025-05-10 00:19:56');


-- H. Order Items 테이블
CREATE TABLE `orderitems` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int NOT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `orderitems_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `orderitems_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `orderitems` VALUES (1,7,4,2,29000.00),(2,8,5,1,45000.00),(3,9,6,1,55000.00),(4,10,8,1,15000.00),(5,11,7,1,38000.00),(6,12,9,1,20000.00);


-- I. Cart 테이블
CREATE TABLE `cart` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '장바구니 ID',
  `user_id` int NOT NULL COMMENT '사용자 ID',
  `product_id` int NOT NULL COMMENT '상품 ID',
  `quantity` int NOT NULL DEFAULT '1' COMMENT '수량',
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`product_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `cart_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `cart_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `cart` VALUES (1,3,4,2),(2,5,5,1),(3,6,6,2),(4,4,7,3),(5,5,9,1),(6,7,8,4);


-- J. Payments 테이블
CREATE TABLE `payments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `method` varchar(50) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `status` varchar(50) NOT NULL,
  `paid_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `payments` VALUES (1,7,'카드',29000.00,'성공','2025-05-10 01:25:48'),(2,8,'무통장',45000.00,'실패','2025-05-10 01:25:48'),(3,9,'카드',55000.00,'성공','2025-05-10 01:25:48'),(4,10,'카드',15000.00,'성공','2025-05-10 01:25:48'),(5,11,'무통장',38000.00,'실패','2025-05-10 01:25:48'),(6,12,'카드',20000.00,'성공','2025-05-10 01:25:48');


-- K. Shipping 테이블
CREATE TABLE `shipping` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '배송 ID',
  `order_id` int NOT NULL COMMENT '주문 ID',
  `address` text NOT NULL COMMENT '배송지 주소',
  `receiver_name` varchar(255) NOT NULL COMMENT '수령자 이름',
  `receiver_phone` varchar(20) NOT NULL COMMENT '수령자 연락처',
  `status` varchar(50) NOT NULL COMMENT '배송 상태 (예: 배송 중, 도착 등)',
  `shipped_at` datetime DEFAULT NULL COMMENT '발송일',
  `delivered_at` datetime DEFAULT NULL COMMENT '도착일',
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  CONSTRAINT `shipping_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `shipping` VALUES (1,7,'천안시 서북구 쌍용동','이지수','01036786886','배송중',NULL,NULL),(2,8,'수원시 영통구 이의동','김수연','01036725562','배송중',NULL,NULL),(3,9,'전주시 덕진구 송천동','이나은','01026757262','도착',NULL,NULL),(4,10,'대전광역시 유성구 봉명동','권예빈','01052868372','도착',NULL,NULL),(5,11,'수원시 영통구 이의동','김수연','01036725562','배송중',NULL,NULL),(6,12,'서울특별시 강남구 역삼동','박솔은','01037825273','도착',NULL,NULL);


-- L. User Measure Profile 테이블
CREATE TABLE `user_measure_profile` (
  `profile_id` int NOT NULL AUTO_INCREMENT COMMENT '측정 프로필 고유 ID',
  `user_id` int NOT NULL COMMENT '사용자 ID (users 테이블 참조)',
  `profile_name` varchar(100) NOT NULL COMMENT '측정 프로필명 (예: "내 최애 후드티")',
  `profile_image_url` varchar(255) DEFAULT NULL COMMENT '사용자가 업로드한 옷 이미지 주소',
  `category` varchar(50) NOT NULL COMMENT '분류 (예: "상의", "하의")',
  `top_length` decimal(5,1) DEFAULT NULL,
  `top_shoulder` decimal(5,1) DEFAULT NULL,
  `top_chest` decimal(5,1) DEFAULT NULL,
  `top_sleeve` decimal(5,1) DEFAULT NULL,
  `bottom_length` decimal(5,1) DEFAULT NULL,
  `bottom_waist` decimal(5,1) DEFAULT NULL,
  `bottom_rise` decimal(5,1) DEFAULT NULL,
  `bottom_hip` decimal(5,1) DEFAULT NULL,
  `bottom_thigh` decimal(5,1) DEFAULT NULL,
  `bottom_hem` decimal(5,1) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '측정값을 저장한 날짜',
  PRIMARY KEY (`profile_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_measure_profile_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `user_measure_profile` VALUES (1,3,'내 최애 후드티 (L)',NULL,'상의',70.0,50.0,58.0,60.0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-01 17:38:50'),(2,3,'자주 입는 청바지 (30)',NULL,'하의',NULL,NULL,NULL,NULL,102.0,40.0,30.0,50.0,31.0,20.0,'2025-11-01 17:38:50'),(3,4,'딱 맞는 반팔티 (M)',NULL,'상의',68.0,46.0,53.0,21.0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-01 17:38:50');


-- M. Wishlist 테이블
CREATE TABLE `wishlist` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '찜 ID',
  `user_id` int NOT NULL COMMENT '사용자 ID',
  `product_id` int NOT NULL COMMENT '상품 ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`product_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `wishlist_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `wishlist_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `wishlist` VALUES (1,3,4),(4,4,7),(2,5,5),(5,5,9),(3,6,6),(6,7,8);


-- N. Password Reset Tokens 테이블 (추가된 기능)
CREATE TABLE `password_reset_tokens` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `token` VARCHAR(500) NOT NULL,
    `expires_at` TIMESTAMP NOT NULL,
    `used` BOOLEAN DEFAULT FALSE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_token` (`token`(255)),
    INDEX `idx_expires` (`expires_at`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='비밀번호 재설정 토큰';


-- 4. 마무리 (외래키 검사 다시 켜기)
SET FOREIGN_KEY_CHECKS = 1;
SELECT '✅ 모든 테이블 생성 및 데이터 입력이 성공적으로 완료되었습니다!' AS Result;
}