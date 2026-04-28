"""
TSIS 1 — PhoneBook Extended
Builds on Practice 7 & 8.  Only NEW functionality is implemented here.
"""

import csv
import json
import psycopg2
from config import load_config



def _conn():
    """Return a live psycopg2 connection."""
    return psycopg2.connect(**load_config())


def _resolve_group(cur, group_name: str) -> int:
    """Return group id, creating the group if it does not exist."""
    cur.execute("SELECT id FROM groups WHERE name = %s;", (group_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "INSERT INTO groups (name) VALUES (%s) RETURNING id;",
        (group_name,)
    )
    return cur.fetchone()[0]


def _resolve_contact(cur, name: str):
    """Return contact row or None."""
    cur.execute("SELECT id, user_name, email, birthday, group_id FROM contacts WHERE user_name = %s;", (name,))
    return cur.fetchone()



def filter_by_group(group_name: str) -> None:
    """Show all contacts in a given group."""
    sql = """
        SELECT c.id, c.user_name, c.email, c.birthday, g.name AS grp
        FROM   contacts c
        LEFT   JOIN groups g ON g.id = c.group_id
        WHERE  g.name ILIKE %s
        ORDER  BY c.user_name;
    """
    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (group_name,))
                rows = cur.fetchall()
                if not rows:
                    print(f"No contacts found in group '{group_name}'.")
                    return
                _print_contacts(cur, rows)
    except Exception as e:
        print("Error:", e)


def search_by_email(email_fragment: str) -> None:
    """Partial-match search on e-mail address."""
    sql = """
        SELECT c.id, c.user_name, c.email, c.birthday, g.name AS grp
        FROM   contacts c
        LEFT   JOIN groups g ON g.id = c.group_id
        WHERE  c.email ILIKE %s
        ORDER  BY c.user_name;
    """
    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, ('%' + email_fragment + '%',))
                rows = cur.fetchall()
                if not rows:
                    print(f"No contacts found for email fragment '{email_fragment}'.")
                    return
                _print_contacts(cur, rows)
    except Exception as e:
        print("Error:", e)


def list_contacts_sorted(sort_by: str = 'name') -> None:
    """
    List all contacts sorted by:
      'name'     → user_name ASC
      'birthday' → birthday ASC (NULLs last)
      'date'     → created_at ASC
    """
    sort_map = {
        'name':     'c.user_name ASC',
        'birthday': 'c.birthday ASC NULLS LAST',
        'date':     'c.created_at ASC',
    }
    order_clause = sort_map.get(sort_by, 'c.user_name ASC')

    sql = f"""
        SELECT c.id, c.user_name, c.email, c.birthday, g.name AS grp
        FROM   contacts c
        LEFT   JOIN groups g ON g.id = c.group_id
        ORDER  BY {order_clause};
    """
    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                if not rows:
                    print("PhoneBook is empty.")
                    return
                _print_contacts(cur, rows)
    except Exception as e:
        print("Error:", e)


def _print_contacts(cur, rows) -> None:
    """Pretty-print a list of (id, name, email, birthday, group) rows."""
    print(f"\n{'ID':<5} {'Name':<20} {'Email':<30} {'Birthday':<12} {'Group':<10}")
    print("-" * 80)
    for row in rows:
        cid, name, email, birthday, grp = row
        # Fetch phones for this contact
        cur.execute(
            "SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY id;",
            (cid,)
        )
        phones = cur.fetchall()
        phone_str = ", ".join(f"{p}({t})" for p, t in phones) if phones else "—"
        print(
            f"{cid:<5} {(name or '—'):<20} {(email or '—'):<30} "
            f"{str(birthday or '—'):<12} {(grp or '—'):<10}"
        )
        print(f"       Phones: {phone_str}")
    print()




def paginated_browse(page_size: int = 5) -> None:
    """Interactive page navigator — next / prev / quit."""
    offset = 0

   
    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM contacts;")
                total = cur.fetchone()[0]
    except Exception as e:
        print("Error:", e)
        return

    if total == 0:
        print("PhoneBook is empty.")
        return

    while True:
        try:
            with _conn() as conn:
                with conn.cursor() as cur:
                    
                    cur.execute(
                        "SELECT * FROM get_users_page(%s, %s);",
                        (page_size, offset)
                    )
                    rows = cur.fetchall()

            if not rows:
                print("No more contacts.")
            else:
                page_num = offset // page_size + 1
                total_pages = (total + page_size - 1) // page_size
                print(f"\n--- Page {page_num}/{total_pages} ---")
                for row in rows:
                    print(f"  ID:{row[0]}  Name:{row[1]}  Phone:{row[2]}")
                print()

            cmd = input("Command [next / prev / quit]: ").strip().lower()

            if cmd == 'next':
                if offset + page_size < total:
                    offset += page_size
                else:
                    print("Already on the last page.")
            elif cmd == 'prev':
                if offset >= page_size:
                    offset -= page_size
                else:
                    print("Already on the first page.")
            elif cmd == 'quit':
                break
            else:
                print("Unknown command — use next / prev / quit.")

        except Exception as e:
            print("Error:", e)
            break



def export_to_json(filepath: str = 'contacts_export.json') -> None:
    """Write all contacts (with phones and group) to a JSON file."""
    sql = """
        SELECT c.id, c.user_name, c.email,
               TO_CHAR(c.birthday, 'YYYY-MM-DD') AS birthday,
               g.name AS grp,
               TO_CHAR(c.created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at
        FROM   contacts c
        LEFT   JOIN groups g ON g.id = c.group_id
        ORDER  BY c.id;
    """
    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                contact_rows = cur.fetchall()

                contacts = []
                for cid, name, email, birthday, grp, created_at in contact_rows:
                    cur.execute(
                        "SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY id;",
                        (cid,)
                    )
                    phones = [{"phone": p, "type": t} for p, t in cur.fetchall()]
                    contacts.append({
                        "id":         cid,
                        "user_name":  name,
                        "email":      email,
                        "birthday":   birthday,
                        "group":      grp,
                        "created_at": created_at,
                        "phones":     phones,
                    })

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(contacts, f, ensure_ascii=False, indent=2)

        print(f"Exported {len(contacts)} contacts → {filepath}")

    except Exception as e:
        print("Error:", e)



def import_from_json(filepath: str = 'contacts_export.json') -> None:
    """
    Read contacts from a JSON file and insert them.
    On duplicate name → prompt: skip / overwrite.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            contacts = json.load(f)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return

    inserted = updated = skipped = 0

    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                for c in contacts:
                    name     = c.get('user_name', '').strip()
                    email    = c.get('email')
                    birthday = c.get('birthday')
                    grp_name = c.get('group')
                    phones   = c.get('phones', [])

                    if not name:
                        print("Skipping entry with no user_name.")
                        skipped += 1
                        continue

                    group_id = _resolve_group(cur, grp_name) if grp_name else None

                    existing = _resolve_contact(cur, name)

                    if existing:
                        answer = input(
                            f"Contact '{name}' already exists. [s]kip / [o]verwrite? "
                        ).strip().lower()
                        if answer != 'o':
                            print(f"  → Skipped '{name}'.")
                            skipped += 1
                            continue

                        cur.execute(
                            """UPDATE contacts
                               SET email = %s, birthday = %s, group_id = %s
                               WHERE user_name = %s RETURNING id;""",
                            (email, birthday or None, group_id, name)
                        )
                        contact_id = cur.fetchone()[0]
                        
                        cur.execute("DELETE FROM phones WHERE contact_id = %s;", (contact_id,))
                        for ph in phones:
                            cur.execute(
                                "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s);",
                                (contact_id, ph['phone'], ph.get('type', 'mobile'))
                            )
                        updated += 1
                        print(f"  → Updated '{name}'.")

                    else:
                        cur.execute(
                            """INSERT INTO contacts (user_name, email, birthday, group_id)
                               VALUES (%s, %s, %s, %s) RETURNING id;""",
                            (name, email, birthday or None, group_id)
                        )
                        contact_id = cur.fetchone()[0]
                        for ph in phones:
                            cur.execute(
                                "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s);",
                                (contact_id, ph['phone'], ph.get('type', 'mobile'))
                            )
                        inserted += 1
                        print(f"  → Inserted '{name}'.")

                conn.commit()

    except Exception as e:
        print("Error:", e)

    print(f"\nDone — inserted: {inserted}, updated: {updated}, skipped: {skipped}")




def import_from_csv(filepath: str = 'contacts.csv') -> None:
    """
    Extended CSV importer.
    Expected columns: user_name, phone, phone_type, email, birthday, group
    phone_type defaults to 'mobile' if blank.
    birthday format: YYYY-MM-DD (blank allowed).
    On duplicate name → skip silently (use import_from_json for overwrite).
    """
    incorrect = []

    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                with open(filepath, newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    inserted = 0

                    for row in reader:
                        name       = row.get('user_name', '').strip()
                        phone      = row.get('phone', '').strip()
                        phone_type = row.get('phone_type', 'mobile').strip() or 'mobile'
                        email      = row.get('email', '').strip() or None
                        birthday   = row.get('birthday', '').strip() or None
                        grp_name   = row.get('group', 'Other').strip() or 'Other'

                        # Validate
                        if not name:
                            incorrect.append(row)
                            continue
                        if not phone.isdigit() or len(phone) < 10:
                            incorrect.append(row)
                            continue
                        if phone_type not in ('home', 'work', 'mobile'):
                            phone_type = 'mobile'

                        group_id = _resolve_group(cur, grp_name)

                        existing = _resolve_contact(cur, name)
                        if existing:
                           
                            contact_id = existing[0]
                        else:
                            cur.execute(
                                """INSERT INTO contacts (user_name, email, birthday, group_id)
                                   VALUES (%s, %s, %s, %s) RETURNING id;""",
                                (name, email, birthday, group_id)
                            )
                            contact_id = cur.fetchone()[0]
                            inserted += 1

                        cur.execute(
                            "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s);",
                            (contact_id, phone, phone_type)
                        )

                conn.commit()

        print(f"CSV import done — {inserted} new contacts.")
        if incorrect:
            print(f"Skipped {len(incorrect)} invalid row(s):")
            for r in incorrect:
                print(" ", r)

    except FileNotFoundError:
        print(f"File not found: {filepath}")
    except Exception as e:
        print("Error:", e)



MENU = """
 1. Filter by group              
 2. Search by e-mail             
 3. List contacts (sorted)       
 4. Browse pages                 
 5. Export to JSON               
 6. Import from JSON             
 7. Import from CSV              
 0. Exit                         

"""


def main():
    while True:
        print(MENU)
        choice = input("Choice: ").strip()

        if choice == '1':
            grp = input("Group name (Family / Work / Friend / Other / custom): ").strip()
            filter_by_group(grp)

        elif choice == '2':
            fragment = input("E-mail fragment to search: ").strip()
            search_by_email(fragment)

        elif choice == '3':
            by = input("Sort by [name / birthday / date]: ").strip().lower() or 'name'
            list_contacts_sorted(by)

        elif choice == '4':
            try:
                size = int(input("Page size (default 5): ").strip() or '5')
            except ValueError:
                size = 5
            paginated_browse(size)

        elif choice == '5':
            path = input("Output file (default contacts_export.json): ").strip() \
                   or 'contacts_export.json'
            export_to_json(path)

        elif choice == '6':
            path = input("JSON file to import (default contacts_export.json): ").strip() \
                   or 'contacts_export.json'
            import_from_json(path)

        elif choice == '7':
            path = input("CSV file to import (default contacts.csv): ").strip() \
                   or 'contacts.csv'
            import_from_csv(path)

        elif choice == '0':
            print("Goodbye!")
            break

        else:
            print("Unknown option. Try again.")


if __name__ == '__main__':
    main()