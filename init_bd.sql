drop database if exists geogesser;
create database if not exists geogesser;
use geogesser;

drop table if exists locations;
create table if not exists locations(
    id_location int primary key auto_increment,
    id_image bigint not null,
    latitude float not null,
    longitude float not null
);

drop table if exists users;
create table if not exists users(
    id_user int primary key auto_increment,
    nickname varchar(255) not null unique,
    email varchar(255) not null unique,
    hashed_password varchar(255) not null,
    created_at datetime default(current_timestamp)
);

drop table if exists rooms;
create table if not exists rooms(
    id_room int primary key auto_increment,
    code varchar(255) not null unique,
    host_id int not null,
    guest_id int not null,
    is_active boolean default(TRUE),
    created_at datetime default(current_timestamp),
    foreign key (host_id) references users(id_user),
    foreign key (guest_id) references users(id_user)
);

drop table if exists room_rounds;
CREATE TABLE if not exists room_rounds (
    id INT PRIMARY KEY AUTO_INCREMENT,
    room_id INT NOT NULL,
    location_id INT NOT NULL,

    host_guess_lat FLOAT,
    host_guess_lon FLOAT,
    guest_guess_lat FLOAT,
    guest_guess_lon FLOAT,

    host_distance_km FLOAT,
    guest_distance_km FLOAT,

    FOREIGN KEY (room_id) REFERENCES rooms(id_room),
    FOREIGN KEY (location_id) REFERENCES locations(id_location)
);

select count(*) row_count from locations;
