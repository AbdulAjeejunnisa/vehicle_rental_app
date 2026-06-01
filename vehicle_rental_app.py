# ============================================================
# VEHICLE RENTAL MANAGEMENT SYSTEM
# Streamlit Frontend + SQLite Backend (Cross-Platform)
#
# INSTALL:  pip install streamlit pandas
# RUN:      streamlit run vehicle_rental_app.py
#
# Works on Windows, Mac, Linux — no SQL Server needed!
# Database file (rental.db) is auto-created on first run.
# ============================================================

import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import date, timedelta

# ============================================================
# DATABASE PATH — stored next to this script
# ============================================================
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rental.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def run_query(sql, params=()):
    conn = get_conn()
    df = pd.read_sql_query(sql, conn, params=params if params else None)
    conn.close()
    return df

def run_write(sql, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params)
    last_id = cur.lastrowid
    conn.commit()
    conn.close()
    return last_id

# ============================================================
# DATABASE INITIALISATION — creates tables + sample data
# ============================================================
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS Vehicle_Categories (
            category_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            email       TEXT,
            phone       TEXT,
            address     TEXT,
            license_no  TEXT
        );

        CREATE TABLE IF NOT EXISTS Employees (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            role        TEXT,
            phone       TEXT
        );

        CREATE TABLE IF NOT EXISTS Vehicles (
            vehicle_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id  INTEGER REFERENCES Vehicle_Categories(category_id),
            brand        TEXT NOT NULL,
            model        TEXT NOT NULL,
            year         INTEGER,
            reg_number   TEXT UNIQUE,
            color        TEXT,
            fuel_type    TEXT,
            seating_cap  INTEGER,
            rent_per_day REAL,
            status       TEXT DEFAULT 'Available'
        );

        CREATE TABLE IF NOT EXISTS Rentals (
            rental_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id  INTEGER REFERENCES Customers(customer_id),
            vehicle_id   INTEGER REFERENCES Vehicles(vehicle_id),
            employee_id  INTEGER REFERENCES Employees(employee_id),
            start_date   TEXT,
            end_date     TEXT,
            total_days   INTEGER,
            total_amount REAL,
            status       TEXT DEFAULT 'Active'
        );

        CREATE TABLE IF NOT EXISTS Payments (
            payment_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            rental_id    INTEGER REFERENCES Rentals(rental_id),
            amount       REAL,
            method       TEXT,
            payment_date TEXT,
            status       TEXT DEFAULT 'Pending'
        );

        CREATE TABLE IF NOT EXISTS Maintenance (
            maint_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER REFERENCES Vehicles(vehicle_id),
            description TEXT,
            cost        REAL,
            maint_date  TEXT
        );
    """)

    # Seed sample data only if tables are empty
    if cur.execute("SELECT COUNT(*) FROM Vehicle_Categories").fetchone()[0] == 0:
        cur.executescript("""
            INSERT INTO Vehicle_Categories (category_name) VALUES
                ('Sedan'), ('SUV'), ('Hatchback'), ('Luxury'), ('Van');

            INSERT INTO Employees (name, role, phone) VALUES
                ('Ravi Kumar',   'Manager',  '9800000001'),
                ('Priya Sharma', 'Staff',    '9800000002'),
                ('Anil Reddy',   'Driver',   '9800000003');

            INSERT INTO Customers (name, email, phone, address, license_no) VALUES
                ('Suresh Babu',   'suresh@email.com',  '9901111111', 'Hyderabad', 'AP0120230001'),
                ('Kavita Singh',  'kavita@email.com',  '9902222222', 'Bangalore', 'KA0220230002'),
                ('Farhan Qureshi','farhan@email.com',  '9903333333', 'Mumbai',    'MH0320230003');

            INSERT INTO Vehicles (category_id,brand,model,year,reg_number,color,fuel_type,seating_cap,rent_per_day,status)
            VALUES
                (1,'Maruti','Swift Dzire',2022,'AP09AB1234','White',  'Petrol',  5, 1200,'Available'),
                (2,'Toyota','Innova',     2021,'AP09CD5678','Silver', 'Diesel',  7, 2500,'Available'),
                (3,'Hyundai','i20',       2023,'AP09EF9012','Red',    'Petrol',  5,  900,'Available'),
                (4,'Mercedes','C-Class',  2022,'AP09GH3456','Black',  'Petrol',  5, 8000,'Available'),
                (5,'Force','Traveller',   2020,'AP09IJ7890','White',  'Diesel', 12, 3500,'Available');
        """)

    conn.commit()
    conn.close()

init_db()

# ============================================================
# APP CONFIG
# ============================================================
st.set_page_config(
    page_title="Vehicle Rental System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
.section-header {
    font-size:1.05rem; font-weight:600; color:#4f46e5;
    border-left:4px solid #4f46e5;
    padding-left:10px; margin:14px 0 8px 0;
}
.pay-success {
    background:#d1fae5; border:1px solid #6ee7b7;
    border-radius:10px; padding:1rem; margin:1rem 0;
    color:#065f46; font-weight:600;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# ADMIN LOGIN
# ============================================================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "rental@2024"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("""
    <div style='text-align:center; padding:2rem 0 1rem 0;'>
        <span style='font-size:3.5rem;'>🚗</span>
        <h1 style='color:#4f46e5; margin:0.5rem 0 0 0;'>Vehicle Rental System</h1>
        <p style='color:#6b7280;'>Please login to access the dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 1.5, 1])
    with col_m:
        st.markdown("---")
        username = st.text_input("👤 Username", placeholder="Enter username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter password")
        login_btn = st.button("🔐 Login", type="primary", use_container_width=True)

        if login_btn:
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.success("✅ Login successful! Redirecting...")
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")

        st.markdown("""
        <div style='text-align:center; margin-top:1rem; color:#9ca3af; font-size:0.8rem;'>
            Default credentials — Username: <b>admin</b> | Password: <b>rental@2024</b>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown("## 🚗 Vehicle Rental")
st.sidebar.markdown("**Management System**")
st.sidebar.divider()
pages = {
    "🏠  Dashboard":   "dashboard",
    "📂  All Tables":  "tables",
    "👥  Customers":   "customers",
    "🚙  Vehicles":    "vehicles",
    "📋  Rentals":     "rentals",
    "💳  Payments":    "payments",
    "🔧  Maintenance": "maintenance",
    "📊  Reports":     "reports",
}
choice = st.sidebar.radio("Navigate", list(pages.keys()), label_visibility="collapsed")
page   = pages[choice]
st.sidebar.divider()
st.sidebar.success(f"✅ Connected\n`rental.db` (SQLite)")
st.sidebar.caption("Cross-platform — no SQL Server needed")
st.sidebar.divider()
st.sidebar.markdown(f"👤 Logged in as **{ADMIN_USERNAME}**")
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# ============================================================
# DASHBOARD
# ============================================================
if page == "dashboard":
    st.title("🚗 Vehicle Rental Management System")
    st.caption("Live data from SQLite database")
    st.divider()

    total_v  = run_query("SELECT COUNT(*) AS c FROM Vehicles")["c"][0]
    avail_v  = run_query("SELECT COUNT(*) AS c FROM Vehicles WHERE status='Available'")["c"][0]
    rented_v = run_query("SELECT COUNT(*) AS c FROM Vehicles WHERE status='Rented'")["c"][0]
    total_c  = run_query("SELECT COUNT(*) AS c FROM Customers")["c"][0]
    active_r = run_query("SELECT COUNT(*) AS c FROM Rentals WHERE status='Active'")["c"][0]
    revenue  = run_query("SELECT IFNULL(SUM(amount),0) AS r FROM Payments WHERE status='Paid'")["r"][0]

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("🚙 Vehicles",  total_v)
    c2.metric("✅ Available",  avail_v)
    c3.metric("🔑 Rented",    rented_v)
    c4.metric("👥 Customers", total_c)
    c5.metric("📋 Rentals",   active_r)
    c6.metric("💰 Revenue ₹", f"{revenue:,.0f}")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-header">Recent Rentals</p>', unsafe_allow_html=True)
        df = run_query("""
            SELECT R.rental_id AS ID, C.name AS Customer,
                   V.brand||' '||V.model AS Vehicle,
                   R.start_date, R.end_date,
                   R.total_amount AS [Amount Rs], R.status
            FROM Rentals R
            JOIN Customers C ON C.customer_id=R.customer_id
            JOIN Vehicles  V ON V.vehicle_id=R.vehicle_id
            ORDER BY R.rental_id DESC LIMIT 8
        """)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with col2:
        st.markdown('<p class="section-header">Vehicle Status</p>', unsafe_allow_html=True)
        df2 = run_query("""
            SELECT status AS Status, COUNT(*) AS Count
            FROM Vehicles GROUP BY status
        """)
        st.dataframe(df2, use_container_width=True, hide_index=True)

        st.markdown('<p class="section-header">Top Vehicles by Rent</p>', unsafe_allow_html=True)
        df3 = run_query("""
            SELECT brand||' '||model AS Vehicle,
                   rent_per_day AS [Rs/Day], status
            FROM Vehicles ORDER BY rent_per_day DESC LIMIT 5
        """)
        st.dataframe(df3, use_container_width=True, hide_index=True)

# ============================================================
# ALL TABLES
# ============================================================
elif page == "tables":
    st.title("📂 All Database Tables")
    st.caption("Direct view from SQLite — rental.db")
    st.divider()
    tables   = ["Vehicle_Categories","Customers","Vehicles","Employees","Rentals","Payments","Maintenance"]
    selected = st.selectbox("📋 Select Table", tables)
    df = run_query(f"SELECT * FROM {selected}")
    st.success(f"**{selected}** — {len(df)} rows, {len(df.columns)} columns")
    st.dataframe(df, use_container_width=True, hide_index=True)

# ============================================================
# CUSTOMERS
# ============================================================
elif page == "customers":
    st.title("👥 Customer Management")
    st.divider()
    tab1, tab2, tab3 = st.tabs(["📋 View All","➕ Add Customer","🔍 Search"])

    with tab1:
        df = run_query("SELECT * FROM Customers ORDER BY customer_id DESC")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"Total: {len(df)} customers")

    with tab2:
        st.markdown('<p class="section-header">Register New Customer</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            name       = st.text_input("Full Name *")
            email      = st.text_input("Email *")
            phone      = st.text_input("Phone *")
        with col2:
            address    = st.text_area("Address", height=70)
            license_no = st.text_input("License No. *")

        if st.button("✅ Add Customer", type="primary"):
            if name and email and phone and license_no:
                try:
                    run_write(
                        "INSERT INTO Customers (name,email,phone,address,license_no) VALUES (?,?,?,?,?)",
                        (name, email, phone, address, license_no)
                    )
                    st.success(f"✅ '{name}' added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.warning("⚠️ Please fill all required fields.")

    with tab3:
        search = st.text_input("🔍 Search by Name or Phone")
        if search:
            df = run_query(
                "SELECT * FROM Customers WHERE name LIKE ? OR phone LIKE ?",
                (f"%{search}%", f"%{search}%")
            )
            st.dataframe(df, use_container_width=True, hide_index=True)

# ============================================================
# VEHICLES
# ============================================================
elif page == "vehicles":
    st.title("🚙 Vehicle Management")
    st.divider()
    tab1, tab2, tab3 = st.tabs(["📋 View Fleet","➕ Add Vehicle","✏️ Update Status"])

    with tab1:
        sf = st.radio("Filter:", ["All","Available","Rented","Maintenance"], horizontal=True)
        base_q = """
            SELECT V.vehicle_id AS ID, VC.category_name AS Category,
                   V.brand, V.model, V.year, V.reg_number AS [Reg No],
                   V.color, V.fuel_type AS Fuel, V.seating_cap AS Seats,
                   V.rent_per_day AS [Rs/Day], V.status
            FROM Vehicles V
            JOIN Vehicle_Categories VC ON VC.category_id=V.category_id
        """
        df = run_query(base_q+" ORDER BY V.vehicle_id" if sf=="All"
                       else base_q+" WHERE V.status=? ORDER BY V.vehicle_id",
                       () if sf=="All" else (sf,))
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"{len(df)} vehicles")

    with tab2:
        st.markdown('<p class="section-header">Add New Vehicle</p>', unsafe_allow_html=True)
        cats    = run_query("SELECT category_id, category_name FROM Vehicle_Categories")
        cat_map = dict(zip(cats["category_name"], cats["category_id"]))
        col1,col2,col3 = st.columns(3)
        with col1:
            cat_name    = st.selectbox("Category *", list(cat_map.keys()))
            brand       = st.text_input("Brand *")
            model       = st.text_input("Model *")
        with col2:
            year        = st.number_input("Year *", 2000, 2026, 2022)
            reg_number  = st.text_input("Reg Number *")
            color       = st.text_input("Color")
        with col3:
            fuel_type   = st.selectbox("Fuel", ["Petrol","Diesel","Electric","CNG"])
            seating_cap = st.number_input("Seats", 1, 20, 5)
            rent_per_day= st.number_input("Rent/Day (₹)*", 100.0, 50000.0, 1500.0, step=100.0)

        if st.button("✅ Add Vehicle", type="primary"):
            if brand and model and reg_number:
                try:
                    run_write("""
                        INSERT INTO Vehicles
                        (category_id,brand,model,year,reg_number,color,fuel_type,seating_cap,rent_per_day)
                        VALUES (?,?,?,?,?,?,?,?,?)
                    """, (cat_map[cat_name], brand, model, int(year), reg_number,
                          color, fuel_type, int(seating_cap), rent_per_day))
                    st.success(f"✅ '{brand} {model}' added!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.warning("⚠️ Please fill all required fields.")

    with tab3:
        v_df  = run_query("SELECT vehicle_id, brand||' '||model||' ['||reg_number||'] - '||status AS label FROM Vehicles")
        v_map = dict(zip(v_df["label"], v_df["vehicle_id"]))
        col1,col2 = st.columns(2)
        with col1:
            v_label    = st.selectbox("Select Vehicle", list(v_map.keys()))
        with col2:
            new_status = st.selectbox("New Status", ["Available","Rented","Maintenance"])
        if st.button("✅ Update", type="primary"):
            run_write("UPDATE Vehicles SET status=? WHERE vehicle_id=?", (new_status, v_map[v_label]))
            st.success(f"✅ Status updated to '{new_status}'!")
            st.rerun()

# ============================================================
# RENTALS
# ============================================================
elif page == "rentals":
    st.title("📋 Rental Management")
    st.divider()
    tab1, tab2, tab3 = st.tabs(["📋 All Rentals","➕ New Rental","🔄 Return Vehicle"])

    with tab1:
        sf = st.radio("Filter:", ["All","Active","Completed","Cancelled"], horizontal=True)
        base = """
            SELECT R.rental_id AS ID, C.name AS Customer,
                   V.brand||' '||V.model AS Vehicle, V.reg_number,
                   R.start_date, R.end_date, R.total_days AS Days,
                   R.total_amount AS [Amount Rs], R.status
            FROM Rentals R
            JOIN Customers C ON C.customer_id=R.customer_id
            JOIN Vehicles  V ON V.vehicle_id=R.vehicle_id
        """
        df = run_query(base+" ORDER BY R.rental_id DESC" if sf=="All"
                       else base+" WHERE R.status=? ORDER BY R.rental_id DESC",
                       () if sf=="All" else (sf,))
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"Total: {len(df)}")

    with tab2:
        st.markdown('<p class="section-header">Create New Rental</p>', unsafe_allow_html=True)
        cust_df  = run_query("SELECT customer_id, name||' ('||phone||')' AS label FROM Customers")
        cust_map = dict(zip(cust_df["label"], cust_df["customer_id"]))
        veh_df   = run_query("""
            SELECT vehicle_id,
                   brand||' '||model||' - Rs.'||CAST(rent_per_day AS INTEGER)||'/day ['||reg_number||']' AS label,
                   rent_per_day
            FROM Vehicles WHERE status='Available'
        """)
        veh_map  = dict(zip(veh_df["label"], veh_df["vehicle_id"]))
        veh_rate = dict(zip(veh_df["label"], veh_df["rent_per_day"]))
        emp_df   = run_query("SELECT employee_id, name||' ('||role||')' AS label FROM Employees")
        emp_map  = dict(zip(emp_df["label"], emp_df["employee_id"]))

        if not veh_map:
            st.warning("⚠️ No available vehicles!")
        else:
            col1,col2 = st.columns(2)
            with col1:
                cust_label = st.selectbox("Customer *", list(cust_map.keys()))
                veh_label  = st.selectbox("Vehicle *",  list(veh_map.keys()))
                emp_label  = st.selectbox("Handled By", list(emp_map.keys()))
            with col2:
                start_date = st.date_input("Start Date *", date.today())
                end_date   = st.date_input("End Date *",   date.today()+timedelta(days=1))
                if end_date > start_date:
                    days   = (end_date - start_date).days
                    amount = days * float(veh_rate[veh_label])
                    st.info(f"📅 **{days} days** | 💰 Total: **₹{amount:,.2f}**")

            if st.button("✅ Create Rental", type="primary"):
                if start_date >= end_date:
                    st.error("❌ End date must be after start date!")
                else:
                    days   = (end_date - start_date).days
                    amount = days * float(veh_rate[veh_label])
                    vid    = veh_map[veh_label]
                    try:
                        rid = run_write("""
                            INSERT INTO Rentals
                            (customer_id,vehicle_id,employee_id,start_date,end_date,total_days,total_amount)
                            VALUES (?,?,?,?,?,?,?)
                        """, (cust_map[cust_label], vid, emp_map[emp_label],
                              str(start_date), str(end_date), days, amount))
                        run_write("UPDATE Vehicles SET status='Rented' WHERE vehicle_id=?", (vid,))
                        run_write("INSERT INTO Payments (rental_id,amount) VALUES (?,?)", (rid, amount))
                        st.success(f"✅ Rental #{rid} created! ₹{amount:,.2f} for {days} days.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

    with tab3:
        active_df = run_query("""
            SELECT R.rental_id,
                   C.name||' → '||V.brand||' '||V.model||' (Due: '||R.end_date||')' AS label,
                   R.vehicle_id
            FROM Rentals R
            JOIN Customers C ON C.customer_id=R.customer_id
            JOIN Vehicles  V ON V.vehicle_id=R.vehicle_id
            WHERE R.status='Active'
        """)
        if active_df.empty:
            st.info("ℹ️ No active rentals.")
        else:
            r_map   = dict(zip(active_df["label"], active_df["rental_id"]))
            v_map   = dict(zip(active_df["label"], active_df["vehicle_id"]))
            r_label = st.selectbox("Select Rental", list(r_map.keys()))
            if st.button("✅ Return Complete", type="primary"):
                run_write("UPDATE Rentals  SET status='Completed' WHERE rental_id=?",  (r_map[r_label],))
                run_write("UPDATE Vehicles SET status='Available' WHERE vehicle_id=?", (v_map[r_label],))
                run_write("UPDATE Payments SET status='Paid'      WHERE rental_id=?",  (r_map[r_label],))
                st.success("✅ Vehicle returned! Payment marked as Paid.")
                st.rerun()

# ============================================================
# PAYMENTS
# ============================================================
elif page == "payments":
    st.title("💳 Payment Management")
    st.divider()
    tab1, tab2, tab3 = st.tabs(["📋 All Payments","➕ Add Payment","✏️ Update Payment"])

    with tab1:
        df = run_query("""
            SELECT P.payment_id AS ID, P.rental_id AS [Rental ID],
                   C.name AS Customer, V.brand||' '||V.model AS Vehicle,
                   P.amount AS [Amount Rs], P.payment_date AS Date,
                   IFNULL(P.method,'—') AS Method, P.status
            FROM Payments P
            JOIN Rentals   R ON R.rental_id=P.rental_id
            JOIN Customers C ON C.customer_id=R.customer_id
            JOIN Vehicles  V ON V.vehicle_id=R.vehicle_id
            ORDER BY P.payment_id DESC
        """)
        st.dataframe(df, use_container_width=True, hide_index=True)
        paid    = run_query("SELECT IFNULL(SUM(amount),0) AS s FROM Payments WHERE status='Paid'")["s"][0]
        pending = run_query("SELECT IFNULL(SUM(amount),0) AS s FROM Payments WHERE status='Pending'")["s"][0]
        c1, c2  = st.columns(2)
        c1.metric("✅ Collected", f"₹{paid:,.2f}")
        c2.metric("⏳ Pending",   f"₹{pending:,.2f}")

    with tab2:
        st.markdown('<p class="section-header">Add Payment Details</p>', unsafe_allow_html=True)
        rental_df = run_query("""
            SELECT R.rental_id,
                   C.name||' → '||V.brand||' '||V.model||
                   ' (Rental #'||R.rental_id||', ₹'||CAST(CAST(R.total_amount AS INTEGER) AS TEXT)||')' AS label,
                   R.total_amount
            FROM Rentals R
            JOIN Customers C ON C.customer_id=R.customer_id
            JOIN Vehicles  V ON V.vehicle_id=R.vehicle_id
            ORDER BY R.rental_id DESC
        """)

        if rental_df.empty:
            st.info("ℹ️ No rentals found to add payment for.")
        else:
            rental_map    = dict(zip(rental_df["label"], rental_df["rental_id"]))
            rental_amount = dict(zip(rental_df["label"], rental_df["total_amount"]))

            col1, col2 = st.columns(2)
            with col1:
                rental_label = st.selectbox("Select Rental *", list(rental_map.keys()), key="add_pay_rental")
                default_amt  = float(rental_amount[rental_label])
                pay_amount   = st.number_input(
                    "Payment Amount (₹) *", min_value=0.0, max_value=9999999.0,
                    value=default_amt, step=100.0, key="add_pay_amount"
                )
            with col2:
                pay_method   = st.selectbox(
                    "Payment Method *",
                    ["Cash","Card","UPI","Net Banking","Cheque","Bank Transfer"],
                    key="add_pay_method"
                )
                pay_date   = st.date_input("Payment Date *", date.today(), key="add_pay_date")
                pay_status = st.selectbox("Payment Status *", ["Paid","Pending","Partial"], key="add_pay_status")

            pay_notes = st.text_area("Notes / Remarks (optional)", height=70, key="add_pay_notes")

            st.markdown(f"""
            <div style='background:#f8faff; border:1.5px solid #c7d2fe; border-radius:12px;
                        padding:1.1rem 1.4rem; margin:1rem 0;'>
                <div style='font-size:0.8rem; color:#6b7280; margin-bottom:0.3rem;'>Payment Summary</div>
                <table style='width:100%; font-size:0.93rem; color:#1e293b;'>
                    <tr><td style='padding:3px 0; color:#64748b;'>Rental</td>
                        <td style='font-weight:600;'>{rental_label}</td></tr>
                    <tr><td style='padding:3px 0; color:#64748b;'>Amount</td>
                        <td style='font-weight:700; color:#4f46e5; font-size:1.1rem;'>₹{pay_amount:,.2f}</td></tr>
                    <tr><td style='padding:3px 0; color:#64748b;'>Method</td>
                        <td>{pay_method}</td></tr>
                    <tr><td style='padding:3px 0; color:#64748b;'>Date</td>
                        <td>{pay_date}</td></tr>
                    <tr><td style='padding:3px 0; color:#64748b;'>Status</td>
                        <td><b>{pay_status}</b></td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

            if st.button("➕ Add Payment", type="primary", use_container_width=True):
                try:
                    rid = rental_map[rental_label]
                    run_write("""
                        INSERT INTO Payments (rental_id, amount, method, payment_date, status)
                        VALUES (?, ?, ?, ?, ?)
                    """, (rid, pay_amount, pay_method, str(pay_date), pay_status))
                    st.success(f"✅ Payment of ₹{pay_amount:,.2f} via {pay_method} added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error adding payment: {e}")

    with tab3:
        st.markdown('<p class="section-header">Update Existing Payment Status</p>', unsafe_allow_html=True)
        pdf = run_query("""
            SELECT P.payment_id,
                   C.name||' — ₹'||CAST(CAST(P.amount AS INTEGER) AS TEXT)||
                   ' via '||IFNULL(P.method,'N/A')||
                   ' (Rental #'||P.rental_id||') — '||P.status AS label,
                   P.method, P.status
            FROM Payments P
            JOIN Rentals   R ON R.rental_id=P.rental_id
            JOIN Customers C ON C.customer_id=R.customer_id
            ORDER BY P.payment_id DESC
        """)
        if pdf.empty:
            st.info("ℹ️ No payments found.")
        else:
            p_map    = dict(zip(pdf["label"], pdf["payment_id"]))
            p_method = dict(zip(pdf["label"], pdf["method"]))
            p_status = dict(zip(pdf["label"], pdf["status"]))

            col1, col2 = st.columns(2)
            with col1:
                p_label    = st.selectbox("Select Payment", list(p_map.keys()), key="upd_pay_sel")
                cur_method = p_method[p_label] if p_method[p_label] else "Cash"
                method_opts = ["Cash","Card","UPI","Net Banking","Cheque","Bank Transfer"]
                method_idx  = method_opts.index(cur_method) if cur_method in method_opts else 0
                new_method  = st.selectbox("Method", method_opts, index=method_idx, key="upd_pay_method")
            with col2:
                status_opts = ["Paid","Pending","Partial"]
                status_idx  = status_opts.index(p_status[p_label]) if p_status[p_label] in status_opts else 1
                new_status  = st.selectbox("Status", status_opts, index=status_idx, key="upd_pay_status")

            if st.button("✅ Update Payment", type="primary"):
                run_write(
                    "UPDATE Payments SET status=?, method=? WHERE payment_id=?",
                    (new_status, new_method, p_map[p_label])
                )
                st.success("✅ Payment updated successfully!")
                st.rerun()

# ============================================================
# MAINTENANCE
# ============================================================
elif page == "maintenance":
    st.title("🔧 Maintenance Records")
    st.divider()
    tab1, tab2 = st.tabs(["📋 View Records","➕ Add Record"])

    with tab1:
        df = run_query("""
            SELECT M.maint_id AS ID, V.brand||' '||V.model AS Vehicle,
                   V.reg_number AS [Reg No], M.maint_date AS Date,
                   M.description AS Description, M.cost AS [Cost Rs]
            FROM Maintenance M
            JOIN Vehicles V ON V.vehicle_id=M.vehicle_id
            ORDER BY M.maint_id DESC
        """)
        st.dataframe(df, use_container_width=True, hide_index=True)
        tc = run_query("SELECT IFNULL(SUM(cost),0) AS c FROM Maintenance")["c"][0]
        st.metric("Total Maintenance Cost", f"₹{tc:,.2f}")

    with tab2:
        veh_df = run_query("SELECT vehicle_id, brand||' '||model||' ['||reg_number||']' AS label FROM Vehicles")
        v_map  = dict(zip(veh_df["label"], veh_df["vehicle_id"]))
        col1,col2 = st.columns(2)
        with col1:
            v_label = st.selectbox("Vehicle *", list(v_map.keys()))
            mdate   = st.date_input("Date", date.today())
        with col2:
            cost    = st.number_input("Cost (₹)", 0.0, 500000.0, 500.0, step=100.0)
            desc    = st.text_area("Description *")
        upd = st.checkbox("Set vehicle status to 'Maintenance'", value=True)
        if st.button("✅ Add Record", type="primary"):
            if desc:
                vid = v_map[v_label]
                run_write("""
                    INSERT INTO Maintenance (vehicle_id,description,cost,maint_date)
                    VALUES (?,?,?,?)
                """, (vid, desc, cost, str(mdate)))
                if upd:
                    run_write("UPDATE Vehicles SET status='Maintenance' WHERE vehicle_id=?", (vid,))
                st.success("✅ Maintenance record added!")
                st.rerun()
            else:
                st.warning("⚠️ Please enter a description.")

# ============================================================
# REPORTS
# ============================================================
elif page == "reports":
    st.title("📊 Reports & Analytics")
    st.divider()
    col1,col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-header">Revenue by Category</p>', unsafe_allow_html=True)
        df1 = run_query("""
            SELECT VC.category_name AS Category,
                   COUNT(R.rental_id) AS Rentals,
                   IFNULL(SUM(R.total_amount),0) AS Revenue
            FROM Vehicle_Categories VC
            LEFT JOIN Vehicles V ON V.category_id=VC.category_id
            LEFT JOIN Rentals  R ON R.vehicle_id=V.vehicle_id
            GROUP BY VC.category_name ORDER BY Revenue DESC
        """)
        st.dataframe(df1, use_container_width=True, hide_index=True)
        if df1["Revenue"].sum() > 0:
            st.bar_chart(df1.set_index("Category")["Revenue"])

    with col2:
        st.markdown('<p class="section-header">Top Customers</p>', unsafe_allow_html=True)
        df2 = run_query("""
            SELECT C.name AS Customer,
                   COUNT(R.rental_id) AS Rentals,
                   IFNULL(SUM(R.total_amount),0) AS TotalSpent
            FROM Customers C
            LEFT JOIN Rentals R ON R.customer_id=C.customer_id
            GROUP BY C.customer_id, C.name ORDER BY Rentals DESC LIMIT 10
        """)
        st.dataframe(df2, use_container_width=True, hide_index=True)

    st.markdown('<p class="section-header">Monthly Summary</p>', unsafe_allow_html=True)
    df3 = run_query("""
        SELECT STRFTIME('%Y-%m', start_date) AS Month,
               COUNT(*) AS TotalRentals,
               IFNULL(SUM(total_amount),0) AS Revenue
        FROM Rentals WHERE status!='Cancelled'
        GROUP BY STRFTIME('%Y-%m', start_date) ORDER BY Month DESC
    """)
    st.dataframe(df3, use_container_width=True, hide_index=True)

    st.markdown('<p class="section-header">Vehicle Utilization</p>', unsafe_allow_html=True)
    df4 = run_query("""
        SELECT V.brand||' '||V.model AS Vehicle, V.reg_number, V.status,
               COUNT(R.rental_id) AS TimesRented,
               IFNULL(SUM(R.total_days),0) AS TotalDays,
               IFNULL(SUM(R.total_amount),0) AS Revenue
        FROM Vehicles V
        LEFT JOIN Rentals R ON R.vehicle_id=V.vehicle_id
        GROUP BY V.vehicle_id, V.brand, V.model, V.reg_number, V.status
        ORDER BY TimesRented DESC
    """)
    st.dataframe(df4, use_container_width=True, hide_index=True)
