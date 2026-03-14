# Mini Banking System

## Objective
Test candidate’s skills in role-based permissions, API design, business logic, exception handling, async tasks, and clean Django coding.

## Overview
This mini banking system has three roles:

| Role           | Access Rights |
|----------------|---------------|
| Customer       | Can view only their own account and loans. Can pay loans. Cannot view other customers. |
| Bank Employee  | Can view all customer accounts but cannot view other employees. |
| Bank Manager   | Can view and manage all accounts, employees, and loans. Can create users but cannot delete or update them. |

The system enforces role-based permissions and handles loans, interest calculations, and account updates.

## Core Concepts
- **Users:** Role-based permissions; Manager can create users.  
- **Bank Accounts:** Track balances; role-based view/edit.  
- **Loans:** Track total, paid amount, and status; validated payments only.

## API Endpoints & Business Rules
1. **View Account Details:** Customer sees own account; Employee sees all customers; Manager sees all.  
2. **Pay Loan:** Reduce loan balance; update status; prevent invalid payments.  
3. **Apply Interest:** Manager only; applies interest to all customer accounts asynchronously.  
4. **Create Users:** Manager only; Employees cannot create users; Managers cannot delete/update users.

## Validation & Exception Handling
- Enforce role-based access  
- Reject invalid operations with clear messages  
- Validate loan payments and account access

## Asynchronous Tasks
- Heavy operations (e.g., interest application) run asynchronously  
- Updated balances are logged

## Summary
This project demonstrates role-based permissions, clean API design, proper business logic, validation, and async operations using Django.
