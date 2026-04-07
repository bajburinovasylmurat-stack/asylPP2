CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    user_name VARCHAR(100),
    phone VARCHAR(20)
);

CREATE OR REPLACE PROCEDURE insert_or_update_user(
    p_name VARCHAR,
    p_phone VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Проверяем существует ли пользователь
    IF EXISTS (
        SELECT 1 FROM users
        WHERE user_name = p_name
    ) THEN

        -- Если существует → обновляем телефон
        UPDATE users
        SET phone = p_phone
        WHERE user_name = p_name;

    ELSE

        -- Если нет → добавляем нового
        INSERT INTO users(user_name, phone)
        VALUES (p_name, p_phone);

    END IF;

END;
$$;

CALL insert_or_update_user('Asyl', '87776481338');
CREATE OR REPLACE PROCEDURE insert_many_users(
    p_names TEXT[],
    p_phones TEXT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
    wrong_data TEXT := '';
BEGIN

   
    FOR i IN 1..array_length(p_names, 1)
    LOOP

        
        IF p_phones[i] ~ '^87[0-9]{9}$' THEN

            
            INSERT INTO users(user_name, phone)
            VALUES (p_names[i], p_phones[i]);


    END LOOP;

    

END;
$$;

CALL insert_many_users(
    ARRAY['Asik', 'Asylmurat', 'Baiburinov'],
    ARRAY['87777777777', '87066481411', '87776665544']
);