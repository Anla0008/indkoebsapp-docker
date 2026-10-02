-- Compose opretter databasen shopping_list og brugeren shopping_app.
-- MariaDB kører dette script automatisk, når datavolumen er tom første gang.
USE shopping_list;

CREATE TABLE IF NOT EXISTS items (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    quantity INT UNSIGNED NOT NULL DEFAULT 1,
    is_bought BOOLEAN NOT NULL DEFAULT FALSE
);
