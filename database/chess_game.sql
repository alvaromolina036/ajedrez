-- Database: chess_game

CREATE DATABASE IF NOT EXISTS chess_game;
USE chess_game;

-- --------------------
-- Table: users
-- --------------------
CREATE TABLE users (
    id INT(11) NOT NULL AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    PRIMARY KEY (id)
);

-- --------------------
-- Table: games
-- --------------------
CREATE TABLE games (
    id INT(11) NOT NULL AUTO_INCREMENT,
    white_user_id INT(11) NOT NULL,
    black_user_id INT(11) NOT NULL,
    active TINYINT(1) NOT NULL DEFAULT 1,
    board_state LONGTEXT DEFAULT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY white_user_id (white_user_id),
    KEY black_user_id (black_user_id)
);

