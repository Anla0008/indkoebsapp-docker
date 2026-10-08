-- Database til indkoebsappen. Eksisterende data slettes ikke.
CREATE DATABASE IF NOT EXISTS to_do
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE to_do;

CREATE TABLE IF NOT EXISTS items (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  quantity INT UNSIGNED NOT NULL DEFAULT 1,
  is_bought BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- En raekke er en vare. Antal er antal pakker/styk.
-- is_bought: 0 = ikke koebt, 1 = koebt.
-- Eksemplerne tilfoejes kun, hvis samme varenavn ikke allerede findes.
INSERT INTO items (name, quantity, is_bought)
SELECT 'Mælk', 2, 0 WHERE NOT EXISTS (SELECT 1 FROM items WHERE name = 'Mælk');
INSERT INTO items (name, quantity, is_bought)
SELECT 'Rugbrød', 1, 0 WHERE NOT EXISTS (SELECT 1 FROM items WHERE name = 'Rugbrød');
INSERT INTO items (name, quantity, is_bought)
SELECT 'Æg', 1, 1 WHERE NOT EXISTS (SELECT 1 FROM items WHERE name = 'Æg');
INSERT INTO items (name, quantity, is_bought)
SELECT 'Bananer', 6, 0 WHERE NOT EXISTS (SELECT 1 FROM items WHERE name = 'Bananer');
INSERT INTO items (name, quantity, is_bought)
SELECT 'Pasta', 2, 1 WHERE NOT EXISTS (SELECT 1 FROM items WHERE name = 'Pasta');
INSERT INTO items (name, quantity, is_bought)
SELECT 'Opvaskemiddel', 1, 0 WHERE NOT EXISTS (SELECT 1 FROM items WHERE name = 'Opvaskemiddel');
