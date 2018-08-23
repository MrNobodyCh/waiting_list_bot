CREATE TABLE IF NOT EXISTS current_password (password VARCHAR);

CREATE TABLE IF NOT EXISTS authorized_users (user_id BIGINT, logged_password VARCHAR);

CREATE TABLE IF NOT EXISTS waiting_list (phone VARCHAR, fullname VARCHAR,
  email VARCHAR, wish_day VARCHAR, wish_time VARCHAR DEFAULT NULL );