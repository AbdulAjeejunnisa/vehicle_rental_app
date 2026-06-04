
# Vehicle Rental App
[![Ask DeepWiki](https://devin.ai/assets/askdeepwiki.png)](https://deepwiki.com/AbdulAjeejunnisa/vehicle_rental_app.git)

A comprehensive Vehicle Rental Management System built with a Streamlit frontend and a SQLite backend. This application provides a user-friendly web interface for managing vehicles, customers, rentals, payments, and maintenance records. It is designed to be cross-platform and requires no external database server, making it easy to run on Windows, macOS, or Linux.

## Features

-   **Live Dashboard**: View key performance indicators (KPIs) like total revenue, vehicle availability, active rentals, and customer count at a glance.
-   **Customer Management**: Add, view, and search for customer records.
-   **Vehicle Fleet Management**: Add new vehicles, update their status (Available, Rented, Maintenance), and view the entire fleet with filtering options.
-   **Rental Management**: Create new rental agreements, link customers to available vehicles, and process vehicle returns.
-   **Payment Tracking**: Log and update payment details and status for each rental.
-   **Maintenance Log**: Keep a record of vehicle maintenance activities and associated costs.
-   **Reporting & Analytics**: Generate reports on revenue by vehicle category, top customers, monthly performance, and vehicle utilization.
-   **Secure Login**: The dashboard is protected by a simple admin login.
-   **Self-Contained Database**: Uses SQLite, which automatically creates the `rental.db` file and populates it with sample data on first launch.

## Technology Stack

-   **Frontend**: Streamlit
-   **Data Handling**: Pandas
-   **Database**: SQLite

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

-   Python 3.7+

### Installation & Setup

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/AbdulAjeejunnisa/vehicle_rental_app.git
    ```

2.  **Navigate to the project directory:**
    ```sh
    cd vehicle_rental_app
    ```

3.  **Install the required dependencies:**
    ```sh
    pip install streamlit pandas
    ```

4.  **Run the application:**
    ```sh
    streamlit run vehicle_rental_app.py
    ```

The application will automatically open in your default web browser.

## Admin Credentials

Use the following default credentials to log in to the management system:

-   **Username:** `admin`
-   **Password:** `rental@2024`
