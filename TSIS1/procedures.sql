-- ============================================================
-- TSIS 1 — Stored Procedures & Functions
-- (Builds on top of Practice 8 — no duplicates)
-- ============================================================

-- ------------------------------------------------------------
-- 3.4.1  add_phone
-- Adds a new phone number to an existing contact.
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR DEFAULT 'mobile'
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    -- Resolve contact
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE user_name = p_contact_name;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    -- Validate phone type
    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type "%". Use home / work / mobile.', p_type;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);

    RAISE NOTICE 'Phone % (%) added to contact "%".', p_phone, p_type, p_contact_name;
END;
$$;


-- ------------------------------------------------------------
-- 3.4.2  move_to_group
-- Moves a contact to a group; creates the group if missing.
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id   INTEGER;
BEGIN
    -- Ensure group exists (create if not)
    INSERT INTO groups (name)
    VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id
    FROM groups
    WHERE name = p_group_name;

    -- Resolve contact
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE user_name = p_contact_name;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    UPDATE contacts
    SET group_id = v_group_id
    WHERE id = v_contact_id;

    RAISE NOTICE 'Contact "%" moved to group "%".', p_contact_name, p_group_name;
END;
$$;


-- ------------------------------------------------------------
-- 3.4.3  search_contacts
-- Full-text pattern search across name, email, and ALL phones.
-- Returns one row per unique contact (uses DISTINCT ON).
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    id        INTEGER,
    user_name VARCHAR,
    email     VARCHAR,
    birthday  DATE,
    grp_name  VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_pattern TEXT := '%' || p_query || '%';
BEGIN
    RETURN QUERY
    SELECT DISTINCT ON (c.id)
           c.id,
           c.user_name,
           c.email,
           c.birthday,
           g.name AS grp_name
    FROM   contacts c
    LEFT   JOIN groups g ON g.id = c.group_id
    LEFT   JOIN phones p ON p.contact_id = c.id
    WHERE  c.user_name ILIKE v_pattern
        OR c.email     ILIKE v_pattern
        OR p.phone     ILIKE v_pattern
    ORDER  BY c.id;
END;
$$;


-- ------------------------------------------------------------
-- Quick smoke-test (comment out after first run)
-- ------------------------------------------------------------
-- CALL add_phone('Asyl', '87009998877', 'work');
-- CALL move_to_group('Asyl', 'Family');
-- SELECT * FROM search_contacts('Asyl');