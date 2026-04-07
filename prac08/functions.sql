CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    user_name VARCHAR(100),
    phone VARCHAR(20)
);
CREATE OR REPLACE FUNCTION get_users_page(
    p_limit INT,
    p_offset INT
)
RETURNS TABLE(
    id INT,
    user_name VARCHAR,
    phone VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT id, user_name, phone
    FROM users
    ORDER BY id
    LIMIT p_limit
    OFFSET p_offset;
END;
$$;
