-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: shopping_app
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cart`
--

DROP TABLE IF EXISTS `cart`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart`
--

LOCK TABLES `cart` WRITE;
/*!40000 ALTER TABLE `cart` DISABLE KEYS */;
INSERT INTO `cart` VALUES (1,3,4,2),(2,5,5,1),(3,6,6,2),(4,4,7,3),(5,5,9,1),(6,7,8,4);
/*!40000 ALTER TABLE `cart` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '카테고리 ID',
  `name` varchar(100) NOT NULL COMMENT '카테고리명',
  `parent_id` int DEFAULT NULL COMMENT '상위 카테고리 ID (nullable)',
  PRIMARY KEY (`id`),
  KEY `parent_id` (`parent_id`),
  CONSTRAINT `categories_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (16,'의류',NULL),(17,'남성 의류',16),(18,'여성 의류',16),(19,'아동 의류',16),(26,'아우터',17),(27,'상의',17),(28,'바지',17),(29,'홈웨어',17),(30,'아우터',18),(31,'상의',18),(32,'바지',18),(33,'원피스',18),(34,'치마',18),(35,'홈웨어',18),(36,'아우터',19),(37,'상의',19),(38,'바지',19),(39,'치마',19),(40,'홈웨어',19);
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orderitems`
--

DROP TABLE IF EXISTS `orderitems`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orderitems`
--

LOCK TABLES `orderitems` WRITE;
/*!40000 ALTER TABLE `orderitems` DISABLE KEYS */;
INSERT INTO `orderitems` VALUES (1,7,4,2,29000.00),(2,8,5,1,45000.00),(3,9,6,1,55000.00),(4,10,8,1,15000.00),(5,11,7,1,38000.00),(6,12,9,1,20000.00);
/*!40000 ALTER TABLE `orderitems` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (7,3,29000.00,'결제완료','2025-05-10 00:19:56'),(8,4,45000.00,'대기','2025-05-10 00:19:56'),(9,7,55000.00,'결제완료','2025-05-10 00:19:56'),(10,5,15000.00,'결제완료','2025-05-10 00:19:56'),(11,6,38000.00,'결제 완료','2025-05-10 00:19:56'),(12,5,20000.00,'대기','2025-05-10 00:19:56');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
INSERT INTO `payments` VALUES (1,7,'카드',29000.00,'성공','2025-05-10 01:25:48'),(2,8,'무통장',45000.00,'실패','2025-05-10 01:25:48'),(3,9,'카드',55000.00,'성공','2025-05-10 01:25:48'),(4,10,'카드',15000.00,'성공','2025-05-10 01:25:48'),(5,11,'무통장',38000.00,'실패','2025-05-10 01:25:48'),(6,12,'카드',20000.00,'성공','2025-05-10 01:25:48');
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_images`
--

DROP TABLE IF EXISTS `product_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_images` (
  `product_image_id` int NOT NULL AUTO_INCREMENT COMMENT '이미지 고유 ID (PK)',
  `product_id` int NOT NULL COMMENT '상품 ID (products.id 참조)',
  `image_url` varchar(255) NOT NULL COMMENT '이미지 경로 또는 URL',
  `image_type` varchar(50) NOT NULL COMMENT '이미지 타입 (예: main, detail)',
  PRIMARY KEY (`product_image_id`),
  KEY `fk_product_images_to_products` (`product_id`),
  CONSTRAINT `fk_product_images_to_products` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='상품별 상세 이미지';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_images`
--

LOCK TABLES `product_images` WRITE;
/*!40000 ALTER TABLE `product_images` DISABLE KEYS */;
/*!40000 ALTER TABLE `product_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_real_measure`
--

DROP TABLE IF EXISTS `product_real_measure`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_real_measure`
--

LOCK TABLES `product_real_measure` WRITE;
/*!40000 ALTER TABLE `product_real_measure` DISABLE KEYS */;
INSERT INTO `product_real_measure` VALUES (1,1,'상의',70.0,45.0,52.5,22.0,NULL,NULL,NULL,NULL,NULL,NULL),(2,2,'상의',72.0,47.0,55.0,23.0,NULL,NULL,NULL,NULL,NULL,NULL),(3,5,'하의',NULL,NULL,NULL,NULL,100.0,38.5,29.0,48.0,30.0,20.0);
/*!40000 ALTER TABLE `product_real_measure` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_size_option`
--

DROP TABLE IF EXISTS `product_size_option`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_size_option` (
  `size_option_id` int NOT NULL AUTO_INCREMENT COMMENT '사이즈 옵션 고유 ID',
  `product_id` int NOT NULL COMMENT '상품 ID (Products 테이블 참조)',
  `option_name` varchar(30) NOT NULL COMMENT '사이즈명 (예: "M", "L", "100")',
  `stock_quantity` int NOT NULL DEFAULT '0' COMMENT '해당 사이즈의 재고 수량',
  PRIMARY KEY (`size_option_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `product_size_option_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_size_option`
--

LOCK TABLES `product_size_option` WRITE;
/*!40000 ALTER TABLE `product_size_option` DISABLE KEYS */;
INSERT INTO `product_size_option` VALUES (1,4,'M',30),(2,4,'L',50),(3,4,'XL',20),(4,4,'XXL',0),(5,5,'28',25),(6,5,'30',30),(7,5,'32',15),(8,6,'Free',30),(9,6,'S',20),(10,6,'M',10),(11,7,'S',25),(12,7,'M',30),(13,7,'L',5);
/*!40000 ALTER TABLE `product_size_option` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (4,'남성 셔츠','캐주얼 스타일의 면 셔츠',29000.00,50,27,'2025-05-09 23:40:11','2025-05-09 23:40:11'),(5,'남성 청바지','슬림핏 데님 바지',45000.00,30,28,'2025-05-09 23:40:11','2025-05-09 23:40:11'),(6,'여성 원피스','봄철용 플라워 패턴 원피스',55000.00,20,32,'2025-05-09 23:40:11','2025-05-09 23:40:11'),(7,'여성 스커트','하이웨이스트 롱 스커트',38000.00,40,33,'2025-05-09 23:40:11','2025-05-09 23:40:11'),(8,'아동 티셔츠','귀여운 캐릭터 프린트 티셔츠',15000.00,100,38,'2025-05-09 23:40:11','2025-05-09 23:40:11'),(9,'아동 청바지','신축성 좋은 아동용 청바지',20000.00,60,39,'2025-05-09 23:40:11','2025-05-09 23:40:11');
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `shipping`
--

DROP TABLE IF EXISTS `shipping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `shipping`
--

LOCK TABLES `shipping` WRITE;
/*!40000 ALTER TABLE `shipping` DISABLE KEYS */;
INSERT INTO `shipping` VALUES (1,7,'천안시 서북구 쌍용동','이지수','01036786886','배송중',NULL,NULL),(2,8,'수원시 영통구 이의동','김수연','01036725562','배송중',NULL,NULL),(3,9,'전주시 덕진구 송천동','이나은','01026757262','도착',NULL,NULL),(4,10,'대전광역시 유성구 봉명동','권예빈','01052868372','도착',NULL,NULL),(5,11,'수원시 영통구 이의동','김수연','01036725562','배송중',NULL,NULL),(6,12,'서울특별시 강남구 역삼동','박솔은','01037825273','도착',NULL,NULL);
/*!40000 ALTER TABLE `shipping` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_measure_profile`
--

DROP TABLE IF EXISTS `user_measure_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_measure_profile`
--

LOCK TABLES `user_measure_profile` WRITE;
/*!40000 ALTER TABLE `user_measure_profile` DISABLE KEYS */;
INSERT INTO `user_measure_profile` VALUES (1,3,'내 최애 후드티 (L)',NULL,'상의',70.0,50.0,58.0,60.0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-01 17:38:50'),(2,3,'자주 입는 청바지 (30)',NULL,'하의',NULL,NULL,NULL,NULL,102.0,40.0,30.0,50.0,31.0,20.0,'2025-11-01 17:38:50'),(3,4,'딱 맞는 반팔티 (M)',NULL,'상의',68.0,46.0,53.0,21.0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-01 17:38:50');
/*!40000 ALTER TABLE `user_measure_profile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (3,'이지수','두두','dodo46@naver.com','6286shj','01036786886','2025-05-09 21:34:49','2025-05-10 12:04:12'),(4,'권예빈','치치','tyeirb@naver.com','yw7whsis','01052868372','2025-05-09 21:34:49','2025-05-10 12:04:12'),(5,'김수연','우유','wyhshsij@naver.com','hsu81@#','01036725562','2025-05-09 21:34:49','2025-05-10 12:04:12'),(6,'이나은','공강 킬러','ohkdha@naver.com','iwy6wy!!','01026757262','2025-05-09 21:34:49','2025-05-10 12:04:12'),(7,'박솔은','자유를 외치다','ciel@naver.com','78eishsj','01037825273','2025-05-09 21:34:49','2025-05-10 12:04:12'),(8,'홍길동','','hong@test.com','81dc9bdb52d04dc20036dbd8313ed055',NULL,'2025-11-01 15:46:51','2025-11-01 15:46:51'),(9,'김영희','','kim@test.com','674f3c2c1a8a6f90461e8a66fb5550ba',NULL,'2025-11-01 15:46:51','2025-11-01 15:46:51');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wishlist`
--

DROP TABLE IF EXISTS `wishlist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wishlist`
--

LOCK TABLES `wishlist` WRITE;
/*!40000 ALTER TABLE `wishlist` DISABLE KEYS */;
INSERT INTO `wishlist` VALUES (1,3,4),(4,4,7),(2,5,5),(5,5,9),(3,6,6),(6,7,8);
/*!40000 ALTER TABLE `wishlist` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- ============================================================
-- 추가 업데이트: 소셜 로그인 및 상품 검색 기능
-- 작성일: 2025-11-26
-- ============================================================

-- 1. products 테이블에 FULLTEXT 인덱스 추가 (상품 검색 기능)
ALTER TABLE products 
ADD FULLTEXT INDEX idx_product_search (name, description);

-- 2. 비밀번호 재설정 토큰 테이블 생성
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='비밀번호 재설정 토큰';

-- 3. 기존 users 테이블 데이터 업데이트 (소셜 로그인 컬럼 NULL 설정)
-- 기존 사용자들의 social_id, social_provider는 NULL로 유지

-- 완료 메시지
SELECT '✅ 데이터베이스 업데이트 완료!' AS message,
       '소셜 로그인 및 상품 검색 기능이 추가되었습니다.' AS detail;

-- Dump completed on 2025-11-14 20:49:08
-- Updated on 2025-11-26 for social login and product search features
