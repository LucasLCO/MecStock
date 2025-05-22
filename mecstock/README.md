# MecStock - Workshop Management and Storage System

## Overview
MecStock is a comprehensive workshop management and storage system designed to streamline the management of services, parts, and costs associated with vehicle maintenance. The application consists of a Django backend and a Streamlit frontend, utilizing PostgreSQL as the database.

## Features
- Manage service orders, including diagnostics, estimates, and service descriptions.
- Handle customer and vehicle registrations.
- Maintain a record of parts and input costs.
- Generate reports on service history and customer interactions.
- Provide a dashboard for monitoring workshop performance and customer returns.

## Project Structure
```
mecstock
├── backend
│   ├── mecstock_project
│   ├── api
│   ├── core
│   ├── manage.py
│   └── requirements.txt
├── frontend
│   ├── app.py
│   ├── pages
│   └── utils
├── docker-compose.yml
├── .env
├── .gitignore
└── README.md
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd mecstock
   ```

2. Set up the backend:
   - Navigate to the `backend` directory.
   - Create a virtual environment and activate it:
     ```
     python -m venv venv
     source venv/bin/activate  # On Windows use `venv\Scripts\activate`
     ```
   - Install the required packages:
     ```
     pip install -r requirements.txt
     ```

3. Set up the frontend:
   - Navigate to the `frontend` directory.
   - Install the required packages:
     ```
     pip install -r requirements.txt
     ```

4. Configure the database:
   - Create a PostgreSQL database and update the `.env` file with the database credentials.

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Start the backend server:
   ```
   python manage.py runserver
   ```

7. Start the Streamlit frontend:
   ```
   streamlit run app.py
   ```

## Usage
- Access the Streamlit frontend through your web browser at `http://localhost:8501`.
- Use the various screens for customer registration, service order management, stock management, and reporting.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.