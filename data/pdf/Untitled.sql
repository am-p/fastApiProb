CREATE TABLE `auth` (
  `user_id` integer,
  `pass_hash` integer,
  `created_at` timestamp
);

CREATE TABLE `users` (
  `id` integer PRIMARY KEY,
  `username` varchar(255),
  `role` varchar(255),
  `email` varchar(255),
  `created_at` timestamp
);

ALTER TABLE `auth` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
