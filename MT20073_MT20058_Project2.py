import sqlite3
from time import sleep
from subprocess import call
from os import system, name
from getpass import getpass
from tabulate import tabulate
from dateutil.relativedelta import relativedelta
from datetime import datetime
from datetime import date

''' CLASS DEFINITIONS '''

class BaseClient:
    ''' object class '''
    def __init__(self,username='',password='',accounts=None):
        ''' constructor '''
        self.__username=username
        self.__password=password
        self.__accounts=list()

    def get_username(self):
        ''' getter '''
        return self.__username

    def get_password(self):
        ''' getter '''
        return self.__password

    def get_accounts(self):
        ''' getter '''
        ''' returns a list of accounts '''
        return self.__acounts

    def set_username(self,username):
        ''' setter '''
        self.__username=username

    def set_password(self,password):
        ''' setter '''
        self.__password=password

    def set_accounts(self,accounts):
        ''' setter '''
        ''' Takes list of accounts, before settings
        remember to get list of accounts  (handle in child class)'''
        self.__accounts=accounts
''' Client Class Definition End '''


class ClientAccManagement(BaseClient):
    ''' service class '''
    def __init__(self):
        super().__init__()
    def add_account(self,category):
        call('clear' if name =='posix' else 'cls')
        print('''
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        $$$$$   Which type of account would you like?  $$$$$
        $$$$$                                          $$$$$
        $$$$$   1. Fixed Deposit                       $$$$$
        $$$$$   2. Savings Deposit                     $$$$$
        $$$$$   3. Loan                                $$$$$
        $$$$$   4. Go Back                             $$$$$
        $$$$$   Enter any option [1..4]                $$$$$
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        ''')
        accounts = super().get_accounts()

        option = input()
        if option == '4':
            print("Thank you, See you soon.")
            sleep(3)
            return None
        #find the value of period...
        elif option == '1':
            fa = FixedAccount()
        elif option == '2':
            sa = SavingAccount()
        elif option == '3':
            la = LoanAccount()
        else:
            return None

    def remove_account(self):
        pass

''' ClientManagement Class End '''
class ClientPassManagement(BaseClient):
    def __init__(self):
        super().__init__()
    def update_password(self,un):
        call('clear' if name =='posix' else 'cls')
        print('''
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        $$$$$          Set New Password!               $$$$$
        $$$$$ Note: Typed passwords wont be displayed  $$$$$
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        ''')
        old_pass = getpass("Enter Existing Password:\t")
        new_pass = getpass("Enter New Password to Set:\t")
        #username = super().get_username()
        username = un
        conn = sqlite3.connect("database.db")
        cr = conn.cursor()
        search_query = "SELECT * FROM accounts WHERE username = ?"
        try:
            a = cr.execute(search_query, (username,))
            record=cr.fetchone()
            if record==None:
                print("No Such Username Exists in our Database")
                sleep(3)
            else:
                if record[2] == old_pass:
                    update_query = "UPDATE accounts SET password = ? WHERE username = ?"
                    try:
                        cr.execute(update_query, (new_pass,username,))
                        print("Password Updated.")
                        sleep(3)
                    except Exception as e:
                        print("Error while Updating Password")
                        print(str(e))
                        conn.rollback()
                else:
                    print("Wrong Old Password Entered")
                    sleep(3)
        except Exception as e:
            print("Error while Searching User")
            print(str(e))
            conn.rollback()
        conn.commit()
        conn.close()

class Client(ClientAccManagement,ClientPassManagement):
    def __init__(self):
        super().__init__()
    def print_details(self):
        pass

class Accounts:
    def __init__(self):
        #self.__acc_type=''
        #self.__amount=0
        #self.__accid=0
        pass
    #ABSTRACT METHOD
    def to_bank(self):
        pass

class SavingAccount(Accounts):
    def __init__(self):
        pass
    def to_bank(self):
        conn = sqlite3.connect("database.db")
        cr = conn.cursor()

        username = input("Enter the Username to Deposit Money:\t")
        search_query = "SELECT * FROM accounts WHERE username = ?"
        try:
            a = cr.execute(search_query, (username,))
            record=cr.fetchone()
            if record==None:
                print("No Such Username Exists in our Database")
                sleep(3)
        except Exception as e:
            print(e)
            conn.close()
            return None
        fetch_id = "SELECT aid FROM accounts WHERE username = ?"
        ids = cr.execute(fetch_id,(username,))
        userid = cr.fetchone()[0]
        amount = input("Enter the Amount to Deposit:\t")

        fetch_amount = "SELECT * FROM deposits as d, accounts as a WHERE d.userid=a.aid and a.username = ?"
        try: # find if already savings deposit exists for the user
            a = cr.execute(fetch_amount,(username,))
            info = cr.fetchone()
            print(info)
            if info == None:
                print("Initial Deposit for User")
                add_amount_query = "INSERT INTO deposits(userid,amount) VALUES(?,?)"
                try:
                    cr.execute(add_amount_query,(userid,amount,))
                    print("Amount Added.")
                    sleep(3)
                except Exception as e:
                    print("Error in creating new savings deposit")
                    print(str(e))
                    sleep(3)
                    conn.rollback()
                update_log_query = "INSERT INTO logs(username,amount) VALUES(?,?)"
                try:
                    cr.execute(update_log_query,(username,amount,))
                    print("Log Updated.")
                    sleep(3)
                except Exception as e:
                    print("Error in updating log")
                    print(str(e))
                    sleep(3)
                    conn.rollback()
            else:
                print("Saving Deposit already Exists for User, Adding new amount...")
                current_amount = int(info[1])
                new_amount = current_amount + int(amount)
                add_amount_query = "UPDATE deposits SET amount = ? WHERE userid = ?"
                try:
                    cr.execute(add_amount_query,(new_amount,userid,))
                    print("Amount Added.")
                    sleep(3)
                except:
                    print("Error in adding money to savings deposit")
                    sleep(3)
                    conn.rollback()
                update_log_query = "INSERT INTO logs(username,amount) VALUES(?,?)"
                try:
                    cr.execute(update_log_query,(username,amount,))
                    print("Log Updated.")
                    sleep(3)
                except Exception as e:
                    print("Error in updating log")
                    print(str(e))
                    sleep(3)
                    conn.rollback()
        except Exception as e:
            print("Error in creating/fetching savings deposit details")
            print(e)
            sleep(3)
            conn.rollback()
        conn.commit() # commit all changes made
        conn.close()
    ''' deposit function end '''

    def from_bank(self):
        '''
            Can be used to withdraw money from saving deposits.
        '''
        conn = sqlite3.connect("database.db")
        cr = conn.cursor()
        call('clear' if name =='posix' else 'cls')
        username = input("Enter the Username to Withdraw Money From:\t")
        get_username = "SELECT * FROM accounts WHERE username=?"
        try:
            cr.execute(get_username,(username,))
            res = cr.fetchone()
            if res == None:
                print("No Such Username")
                sleep(3)
                withdraw_money()
            else:
                fetch_id = "SELECT aid FROM accounts WHERE username = ?"
                ids = cr.execute(fetch_id,(username,))
                userid = cr.fetchone()[0]
                try:
                    amount = int(input("Enter the Amount to Withdraw:\t"))
                except:
                    print("Not valid number")
                    conn.close()
                    return None
                fetch_amount = "SELECT * FROM deposits WHERE userid = ?"
                try: # find if already savings deposit exists for the user
                    a = cr.execute(fetch_amount,(userid,))
                    info = cr.fetchone()
                    if info == None:
                        print("No Deposit exists for User")
                        conn.close()
                        sleep(3)
                        return None
                    else:
                        current_money = info[1] #current amount in database
                        if ( current_money - amount ) < 0:
                            print("Not enough money in Bank")
                            conn.close()
                            sleep(3)
                            return None
                        # if enough amount -> continue
                        add_amount_query = "UPDATE deposits SET amount = ? WHERE userid = ?"
                        new_amount = current_money - amount
                        try:
                            cr.execute(add_amount_query,(new_amount,userid,))
                            print("Amount Updated.")
                            sleep(3)
                        except Exception as e:
                            print("Error in creating new savings deposit")
                            print(str(e))
                            sleep(3)
                            conn.rollback()
                        amount = amount * -1
                        update_log_query = "INSERT INTO logs(username,amount) VALUES(?,?)"
                        try:
                            cr.execute(update_log_query,(username,amount,))
                            print("Log Updated.")
                            sleep(3)
                        except Exception as e:
                            print("Error in updating log")
                            print(str(e))
                            sleep(3)
                            conn.rollback()
                except Exception as e:
                    print("Error in fetching bank details")
                    print(str(e))
                    sleep(3)
        except Exception as e:
            print("Error in fetching username")
            print(str(e))
            sleep(3)

        conn.commit()
        conn.close()
    ''' withdraw function end '''
''' Class SavingAccount End '''

class FixedAccount(Accounts):
    def __init__(self):
        pass
    def to_bank(self):
        call('clear' if name =='posix' else 'cls')
        print('''
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        $$$$$   How long should the fixed deposit be?  $$$$$
        $$$$$                                          $$$$$
        $$$$$   1. Fixed Deposit for 1 Year            $$$$$
        $$$$$   2. Fixed Deposit for 3 Year            $$$$$
        $$$$$   3. Fixed Deposit for 5 and more Years  $$$$$
        $$$$$   4. Go Back                             $$$$$
        $$$$$   Enter any option [1..4]                $$$$$
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        ''')
        option = input()
        if option == '4':
            print("Thank you, See you soon.")
            sleep(3)
            return None
        #find the value of period...
        elif option == '1':
            period = 1
            rate_name = "fixed1"
        elif option == '2':
            period = 3
            rate_name = "fixed3"
        elif option == '3':
            while True:
                period = int(input("Enter the period for fixed deposit(Must be greater than 5 years):\t"))
                if period < 5:
                    print("Entered period is less than or equal to 5:")
                else:
                    break
            rate_name = "fixed5"
        elif int(option) not in range(1,4):
            print("I didn't understand you, try again...")
            sleep(3)
            self.to_bank()
        conn = sqlite3.connect("database.db")
        cr = conn.cursor()

        #username = input("Enter the Username to Deposit Money:\t")
        username = input("ENTER USERNAME:\t")
        search_query = "SELECT * FROM accounts WHERE username = ?"
        try:
            a = cr.execute(search_query, (username,))
            record=cr.fetchone()
            if record==None:
                print("No Such Username Exists in our Database")
                sleep(3)
        except Exception as e:
            print(e)
            conn.close()
            return None
        amount = input("Enter the Amount to Deposit:\t")
        #get Interest
        get_interest_query = "SELECT rate_val FROM rates WHERE rate_name = ?"
        interest = 0
        try:
            cr.execute(get_interest_query,(rate_name,))
            interest = cr.fetchone()
            interest = float(interest[0])
        except Exception as e:
            print("Error in fetching interest rate")
            print(str(e))
            sleep(3)
            conn.rollback()

        #calculate end_date using period
        current_date = date.today()
        end_date = current_date + relativedelta(years=period)
        fetch_id = "SELECT aid FROM accounts WHERE username = ?"
        ids = cr.execute(fetch_id,(username,))
        userid = cr.fetchone()[0]
        add_fixed_amount_query = "INSERT INTO fixed_deposits(user_id,amount,period,end_date,interest) VALUES(?,?,?,?,?)"
        try:
            cr.execute(add_fixed_amount_query,(userid,amount,period,end_date,interest))
            print("Fixed Amount Added.")
            sleep(3)
        except Exception as e:
            print("Error in creating new fixed deposit")
            print(str(e))
            sleep(3)
            conn.rollback()

        conn.commit()
        conn.close()

    def from_bank(self): # need to ask which fixed deposit in case many or different account for each fixed deposit?
        print("BY BANK POLICY YOU ARE NOT ALLOWED TO BREAK FIXED DEPOSIT BEFORE MATURITY DATE")

class LoanAccount(Accounts):
    def request_loan(self):
        pass

class LoanAccountManagement(LoanAccount):
    ''' service class '''
    def accept_emi_payment(self):
        conn = sqlite3.connect("database.db")
        cr = conn.cursor()
        username = input("Enter Username of Client:\t")
        search_query = "SELECT * FROM accounts WHERE username = ?"
        try:
            a = cr.execute(search_query, (username,))
            record=cr.fetchone()
            if record==None:
                print("No Such Username Exists in our Database")
                sleep(3)
        except Exception as e:
            print(e)
            conn.close()
            return None
        fetch_id = "SELECT aid FROM accounts WHERE username = ?"
        ids = cr.execute(fetch_id,(username,))
        userid = cr.fetchone()[0]
        search_loan_requests = "SELECT next_due_date FROM loans as l, accounts as a WHERE l.user__id=a.aid and a.username = ?"
        try:
            cr.execute(search_loan_requests,(username,))
            res = cr.fetchone()
            due_date = datetime.strptime(res[0], '%Y-%m-%d').date()
            new_due_date = due_date + relativedelta(months=1)
            update_due_date = "UPDATE  loans SET next_due_date = ? WHERE user__id = ?"
            try:
                cr.execute(update_due_date,(new_due_date,userid,))
                print("EMI Paid, Due Date Updated")
                sleep(3)
            except Exception as e:
                print(e)
                conn.rollback()
        except Exception as e:
            print("Error in fetching loan requests")
            print(str(e))
            conn.rollback()
        conn.commit()
        conn.close()
    ''' accept_emi_payment function end '''
    ''' service class '''
    def view_loans(self):
        conn = sqlite3.connect("database.db")
        cr = conn.cursor()
        search_loan_requests = "SELECT loan_id, username, amount FROM loans as l, accounts as a where a.aid=l.user__id and loan_status = 0"
        try:
            cr.execute(search_loan_requests)
            record=cr.fetchall()
            call('clear' if name =='posix' else 'cls')
            print(tabulate(record, headers=['Username', 'Amount'], tablefmt='orgtbl'))
            input("Enter any character(s) to Go Back\n")
        except Exception as e:
            print("Error in fetching loan requests")
            print(str(e))
            conn.rollback()
        conn.commit()
        conn.close()
    def accept_loans(self):
        conn = sqlite3.connect("database.db")
        cr = conn.cursor()
        search_loan_requests = "SELECT loan_id, username, amount FROM loans as l, accounts as a where a.aid=l.user__id and loan_status = 0"
        try:
            cr.execute(search_loan_requests)
            record=cr.fetchall()
            call('clear' if name =='posix' else 'cls')
            print(tabulate(record, headers=['username', 'Amount'], tablefmt='orgtbl'))
            print('''
            $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$5$$$$$$$$$$$$$$$$$$$$$
            $$$$$           WELCOME LOANS SECTION          $$$$$
            $$$$$             Choose any option:           $$$$$
            $$$$$      1. Approve any Loan Request         $$$$$
            $$$$$      2. Go Back                          $$$$$
            $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$''')
            option = input("Enter any number in range (1,2):\t")
            if option == '2' or option != '1':
                return None
            print()
            loan_id = input("Enter any loan_id to Approve it\n")
            interest = float(input("Enter Interest to be Set for this loan:\t"))
            period = int(input("Enter the period(in year) for repayment of loan:\t"))
            approve_date = date.today()
            due_date = approve_date + relativedelta(years=period)
            next_due_date = approve_date + relativedelta(months=1)
            amount = 0
            #fetch amount for loan_id
            try:
                get_amount_query = "SELECT amount FROM loans WHERE loan_id = ?"
                cr.execute(get_amount_query,(loan_id,))
                res = cr.fetchone()
                amount = res[0]
            except Exception as e:
                print(e)
            interest = interest / (12 * 100)
            period = period * 12
            emi = (amount * interest * pow(1 + interest, period)) / (pow(1 + interest, period) - 1)
            update_loan_requests = "UPDATE loans SET interest = ?, date_taken = ?, due_date = ?, next_due_date = ?, emi = ?, loan_status = 1 WHERE loan_id = ?"
            try:
                cr.execute(update_loan_requests,(interest,approve_date,due_date,next_due_date,emi,loan_id,))
                print("Approved Loan")
                sleep(3)

            except Exception as e:
                print("Error in approving loan requests")
                print(str(e))
                conn.rollback()

        except Exception as e:
            print("Error in fetching loan requests")
            print(str(e))
            conn.rollback()
        conn.commit()
        conn.close()

''' Class LoanAccountManagement End '''


class OperationalManagement:
    ''' service class '''
    def set_interest_rates(self):
        call('clear' if name =='posix' else 'cls')
        print('''
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        $$$$$          Set Interest For?               $$$$$
        $$$$$                                          $$$$$
        $$$$$   1. Savings accounts                    $$$$$
        $$$$$   2. 1 year Fixed Deposits               $$$$$
        $$$$$   3. 3 year Fixed Deposits               $$$$$
        $$$$$   4. 5+ year Fixed Deposits              $$$$$
        $$$$$   5. Go Back                             $$$$$
        $$$$$   Enter any option [1..5]                $$$$$
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        ''')
        option = input() #Take user input
        conn = sqlite3.connect("database.db")
        cr = conn.cursor() #Create cursor object

        create_table_rates = """CREATE TABLE IF NOT EXISTS rates(
        rate_id INTEGER PRIMARY KEY AUTOINCREMENT,
        rate_name TEXT UNIQUE NOT NULL,
        rate_val REAL NOT NULL
        )"""
        #Note: SQLite understands the column type of "VARCHAR(N)" to be the same as "TEXT"
        try:
            cr.execute(create_table_rates) # Create rates table if not exists
        except Exception as e:
            print("Error in creating 'rates' table")
            print(str(e))
            conn.rollback()
        update_query = "REPLACE INTO rates(rate_name, rate_val) VALUES(?,?)"

        if option == '1':
            rate_val = input("Enter value for interest rate:")
            try:
                cr.execute(update_query, ("savings",rate_val))
                print("Interest rates updated.")
                sleep(3)
            except:
                print("Error while updating rates in 'rates' table")
                conn.rollback()

        elif option == '2':
            rate_val = input("Enter value for interest rate:")
            try:
                cr.execute(update_query, ("fixed1",rate_val))
                print("Interest rates updated.")
                sleep(3)
            except:
                print("Error while updating rates in 'rates' table")
                conn.rollback()

        elif option == '3':
            rate_val = input("Enter value for interest rate:")
            try:
                cr.execute(update_query, ("fixed3",rate_val))
                print("Interest rates updated.")
                sleep(3)
            except:
                print("Error while updating rates in 'rates' table")
                conn.rollback()

        elif option == '4':
            rate_val = input("Enter value for interest rate:")
            try:
                cr.execute(update_query, ("fixed5",rate_val))
                print("Interest rates updated.")
                sleep(3)
            except:
                print("Error while updating rates in 'rates' table")
                conn.rollback()

        elif option == '5':
            return None
        else:
            print("Sorry I didn't understand, make sure you enter number in range [1..5]")
            sleep(3)
            set_interest()
        conn.commit()
        conn.close()
        ''' End of Function set_interest_rates '''
''' End Class OperationalManagement '''

class UserManagement:
    ''' service class '''
    def add_user(self):
        call('clear' if name =='posix' else 'cls')
        print('''
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        $$$$            ENTER /q TO GO BACK            $$$$$
        $$$$         anything else to continue         $$$$$
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        ''')
        option = input()
        if option != '/q':
            username = input("Enter Username for New Account:\t")
            password = getpass("Enter Password for New Account:\t")
            conn = sqlite3.connect("database.db")
            cr = conn.cursor()

            create_table_accounts = """CREATE TABLE IF NOT EXISTS accounts(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
            )"""
            try:
                cr.execute(create_table_accounts) # if accounts table doesnt exists create it
            except Exception as e:
                print("Error in creating 'accounts' table")
                print(str(e))
                conn.rollback()

            update_query = "INSERT INTO accounts(username, password) VALUES(?,?)"
            try:
                cr.execute(update_query, (username,password)) # add new user
                print("Account Added.")
                sleep(3)
            except:
                print("Error while Creating User")
                conn.rollback() #roll back in case of any errors
            conn.commit()
            conn.close()
        else:
            return None# GO BACK
    ''' end of function add_user '''

    def remove_user(self):
        call('clear' if name =='posix' else 'cls')
        print('''
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        $$$$$          ENTER /q TO GO BACK             $$$$$
        $$$$         anything else to continue         $$$$$
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        ''')
        option = input()
        if option != '/q':
            username = input("Enter Username of the Account to be Deleted:\t")
            conn = sqlite3.connect("database.db")
            cr = conn.cursor()

            create_table_accounts = """CREATE TABLE IF NOT EXISTS accounts(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
            )"""
            try:
                cr.execute(create_table_accounts)
            except Exception as e:
                print("Error in creating 'accounts' table")
                print(str(e))
                conn.rollback()
            search_query = "SELECT * FROM accounts WHERE username = ?"
            try:
                a = cr.execute(search_query, (username,))
                record=cr.fetchone()
                if record==None:
                    print("No Such Username Exists in our Database")
                    sleep(3)
                else:
                    update_query = "DELETE FROM accounts WHERE username = ?"
                    try:
                        cr.execute(update_query, (username,))
                        print("Account Deleted.")
                        sleep(3)
                    except:
                        print("Error while Deleting User")
                        conn.rollback()
            except Exception as e:
                print("Error while Searching User")
                print(str(e))
                conn.rollback()
            conn.commit()
            conn.close()
        else:
            return None
    ''' end of function remove_user '''
''' End Class UserManagement '''

class Admin(LoanAccountManagement,OperationalManagement,UserManagement):
    ''' service class '''
    def __init__(self):
        #Code for admin interface
        print('''
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$5$$$$$$$$$$$$$$$$$$$$$
        $$$$$          WELCOME TO MINI BANK            $$$$$
        $$$$$             Admin Panel                  $$$$$
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        Date:''',date.today())
        print('''
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        $$$$$          How may I help you?             $$$$$
        $$$$$                                          $$$$$
        $$$$$   1. Set Interest Rates                  $$$$$
        $$$$$   2. View Customer Summary               $$$$$
        $$$$$   3. View Loan Requests                  $$$$$
        $$$$$   4. Approve Loan Requests               $$$$$
        $$$$$   5. Add User                            $$$$$
        $$$$$   6. Remove User                         $$$$$
        $$$$$   7. Deposit Money                       $$$$$
        $$$$$   8. Withdraw                            $$$$$
        $$$$$   9. View Complaints                     $$$$$
        $$$$$   10. Accept EMI Payment                 $$$$$
        $$$$$   11. Exit                               $$$$$
        $$$$$   Enter any option between[1..11]        $$$$$
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        ''')

        try: #Exception may be generated if user enters non integer value
            option = int(input("Enter:\t"))
            while option not in range(1,12):
                print("Sorry I didn't understand, make sure you enter number in range [1..11]")
                sleep(3)
                call('clear' if name =='posix' else 'cls')
                option = int(input("Enter:\t"))
        except Exception as e:
            print("You entered non integer input")
            print(e)
            self.__init__()
            return None
        if option == 1:
            super().set_interest_rates()
            self.__init__()
        elif option == 2:
            self.view_customer_summary()
            self.__init__()
        elif option == 3:
            super().view_loans()
            self.__init__()
        elif option == 4:
            super().accept_loans()
            self.__init__()
        elif option == 5:
            super().add_user()
            self.__init__()
        elif option == 6:
            super().remove_user()
            self.__init__()
        elif option == 7:
            call('clear' if name =='posix' else 'cls')
            print('''
            $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$5$$$$$$$$$$$$$$$$$$$$$
            $$$$$        WELCOME DEPOSITS    SECTION       $$$$$
            $$$$$             Choose any option:           $$$$$
            $$$$$      1. Savings Deposit                  $$$$$
            $$$$$      2. Fixed Deposit                    $$$$$
            $$$$$      3. Go Back                          $$$$$
            $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$''')
            option = input("Enter any number in range (1,3):\t")

            if option == '1':
                sa = SavingAccount()
                sa.to_bank()
                self.__init__()
            elif option == '2':
                fa = FixedAccount()
                fa.to_bank()
                self.__init__()
            elif option == '3':
                self.__init__()
            else:
                print("I didn't understand you, try again...")
                sleep(3)
        elif option == 8:
            sa = SavingAccount()
            sa.from_bank()
            self.__init__()
        elif option == 9:
            self.view_complaints()
            self.__init__()
        elif option == 10:
            lam = LoanAccountManagement()
            lam.accept_emi_payment()
            self.__init__()
        elif option == 11:
            print("Thank you, Goodbye.")
            sleep(3)
            call('clear' if name =='posix' else 'cls')
            exit(0)
    ''' end of constructor '''

    def view_customer_summary(self):
        '''
            Displays non-performing Clients i.e., clients who haven't payed their dues yet.
        '''
        conn = sqlite3.connect("database.db")
        cr = conn.cursor()
        curr_date = date.today()
        find_non_performing = "SELECT * FROM loans"
        try:
            cr.execute(find_non_performing)
            res = cr.fetchall()
            non_performers = []
            for r in res:
                stored_date = datetime.strptime(r[5], '%Y-%m-%d').date()
                if  stored_date < curr_date: #r[5] = next_due_date, if due_date crossed
                    non_performers.append(r)
            call('clear' if name =='posix' else 'cls')
            print(tabulate(non_performers, headers=['Username', 'Amount','Date Taken','Due Date','Next Due Date','Interest','EMI','Loan Status'], tablefmt='orgtbl'))
            input("{RESS ENTER TO GO BACK\n")

        except Exception as e:
            print(e)
            print("Couldnt fetch non performing clients")
        conn.commit()
        conn.close()
    ''' view_customer_summary function end '''

    def view_complaints(self):
        conn = sqlite3.connect("database.db")
        cr = conn.cursor()
        create_table_complaints = """CREATE TABLE IF NOT EXISTS complaints(
        complaints_id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_text TEXT NOT NULL,
        complaint_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        complaint_status INTEGER NOT NULL DEFAULT 1
        )"""
        #1 in complaint status = active, 0: inactive
        try:
            cr.execute(create_table_complaints)
        except Exception as e:
            print("Error in creating 'complaints' table")
            print(str(e))
            conn.rollback()
        search_complaints = "SELECT complaints_id, complaint_text, complaint_date FROM complaints where complaint_status = 1"
        try:
            cr.execute(search_complaints)
            record=cr.fetchall()
            call('clear' if name =='posix' else 'cls')
            print(tabulate(record, headers=['Complaint Text', 'Complaint Date'], tablefmt='orgtbl'))
            print('''
            $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$5$$$$$$$$$$$$$$$$$$$$$
            $$$$$        WELCOME COMPLAINTS SECTION        $$$$$
            $$$$$             Choose any option:           $$$$$
            $$$$$      1. Mark a Complaint as resolved     $$$$$
            $$$$$      2. Go back                          $$$$$
            $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$''')
            option = input("Enter 1 or 2:\t")
            if option == '1':
                com_id = input("Enter Complaint ID to mark as Resolved:\t")
                update_query = "UPDATE complaints SET complaint_status = 0 WHERE complaints_id = ?"
                try:
                    cr.execute(update_query,(com_id,))
                    print("Resolved the complaint")
                    sleep(3)
                except Exception as e:
                    print("Error in updating complaint_status ")
                    print(str(e))
                    conn.rollback()
        except Exception as e:
            print("Error in fetching 'complaints' table")
            print(str(e))
            conn.rollback()
        conn.commit()
        conn.close()
    ''' view_complaints function end '''
''' Class Admin End '''

class SystemServices:
    ''' service class '''
    def login(self):
        ''' takes Nothing and returns whether logged in Successfully '''
        print('''
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$5$$$$$$$$$$$$$$$$$$$$$
        $$$$$          WELCOME TO MINI BANK            $$$$$
        $$$$$      Please Enter your Credentials       $$$$$
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$''')
        username = input("Enter your username(case-sensitive):\t")
        password = getpass("Enter your password(hidden):\t")

        conn = sqlite3.connect("database.db")
        cr = conn.cursor()

        authorize_query = "SELECT * FROM accounts WHERE username = ?"
        try:
            cr.execute(authorize_query, (username,))
        except Exception as e:
            print("Error during Login - while fetching username")
            print(str(e)) #Print error
            conn.rollback() #Roll back changes made
        record=cr.fetchone() #Fetch one record
        if record==None: #If no record with given username found in database
            print("No such username exists") #print message
            sleep(3) #Sleep the program for 3 seconds
             #clear screen based on whether windows or linux
            conn.close() #close connection
            return False, None #Return false as operation unsuccessful
        else:
            if record[2] == password:

                print("Logged in Successfully")

                sleep(3)

                if record[1] == 'admin':
                    return True, 'admin'
                else:
                    cl = Client()
                    cl.set_username=username
                    cl.set_password=password
                    fetch_id = "SELECT aid FROM accounts WHERE username = ?"
                    ids = cr.execute(fetch_id,(username,))
                    userid = cr.fetchone()[0]
                    #search all saving account and add
                    fetch = "SELECT * FROM deposits WHERE userid = ?"
                    try:
                        abc = cr.execute(fetch_id,(userid,))
                        accou = cr.fetchone()[0]
                        cl.add_account(accou)
                    except:
                        print('no deposit accounts for user')
                    fetch = "SELECT * FROM fixed_deposits WHERE userid = ?"
                    try:
                        abc = cr.execute(fetch_id,(userid,))
                        accou = cr.fetchone()[0]
                        cl.add_account(accou)
                    except:
                        print('no deposit accounts for user')
                    fetch = "SELECT * FROM loans WHERE userid = ?"
                    try:
                        abc = cr.execute(fetch_id,(userid,))
                        accou = cr.fetchone()[0]
                        cl.add_account(accou)
                    except:
                        print('no deposit accounts for user')
                    conn.close()
                    return True, username
            else:
                print("Wrong Passoword! Contact admin if any trouble.")
                sleep(3)
                conn.close()
                return False, '' #Return false as operation unsuccessful
    ''' login function end '''

''' Class SystemServices End '''






# class interface and account management(intrest calculation) code frm here
class Client_Interface(Client):
    """docstring for Client_Interface"""
    def __init__(self, username):
        self.username = username
        # Welcome screen of client interface after log in to client
        print('''
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$5$$$$$$$$$$$$$$$$$$$$$
        $$$$$          WELCOME TO MINI BANK            $$$$$
        $$$$$             User Panel                   $$$$$
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        Date:''',date.today())
        print('''
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        $$$$$          How may I help you?             $$$$$
        $$$$$                                          $$$$$
        $$$$$   1. Check Transactions                  $$$$$
        $$$$$   2. Register Complaint                  $$$$$
        $$$$$   3. Request Loan                        $$$$$
        $$$$$   4. Update Password                     $$$$$
        $$$$$   5. Exit                                $$$$$
        $$$$$   Enter any option between[1..5]         $$$$$
        $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        ''')

        try: #Exception may be generated if user enters non integer value
            option = int(input("Enter:\t"))
            while option not in range(1,6):
                print("Sorry I didn't understand, make sure you enter number in range [1..5]")
                sleep(3)

                option = int(input("Enter:\t"))
        except Exception as e:
            print("You entered non integer input")
            print(e)
            client_interface() #Relaunch interface
            return None

        if option == 1:
            self.check_trans()
            self.__init__(username)
        elif option == 2:
            self.register_complaint()
            self.__init__(username)
        elif option == 3:
            self.request_loan()
            self.__init__(username)
        elif option == 4:
            super().update_password(username)
            self.__init__(username)
        elif option == 5:
            print("Thank you for Banking with us, Goodbye. :-)")
            exit(0)
    ''' End of Function definitions '''

    # Module for registering complaint
    def register_complaint(self):
        # it takes username as arguments and do the work for respective user
        complaint = input("Please enter your complaint here:    ")
        complaint = self.username + ': ' + complaint         #appending username and its complaint to add in database
        conn = sqlite3.connect("database.db")               #making connection to database
        cr = conn.cursor()              #cursor to database
        #creating table if it doesnot exists
        create_table_complaints = """CREATE TABLE IF NOT EXISTS complaints(
        complaints_id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_text TEXT NOT NULL,
        complaint_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        complaint_status INTEGER NOT NULL DEFAULT 1
        )"""
        #1 in complaint status = active, 0: inactive
        #tries to create table if error exists then catches it
        try:
            cr.execute(create_table_complaints)
        except Exception as e:
            print("Error in creating 'complaints' table:    ")
            print(str(e))
            conn.rollback()
        today_date = date.today()
        #query to insert data in database
        update_query = "INSERT INTO complaints(complaint_text, complaint_date, complaint_status) VALUES(?,?,1)"

        #tries to insert data in database if error exists then catches it
        try:
            cr.execute(update_query, (complaint,today_date)) # add data to database
            print("Your Complaint has been registered. Sorry for the inconvenience")
        except Exception as e:
            print("Error while Registering Complaint")
            print(e)
            conn.rollback() #roll back in case of any errors
        sleep(3)    #waiting for 3 secs
        conn.commit()   #commiting the changes to database
        conn.close()    #closing the database connection


    #module for printing all the transactions of a respective user
    def check_trans(self):
        conn = sqlite3.connect("database.db")  #making connection to database
        cr = conn.cursor()  #cursor to database

        #creating table if it doesnot exists
        create_table_logs = """CREATE TABLE IF NOT EXISTS logs(
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        amount INTEGER NOT NULL,
        date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )"""
        try: # build table
            cr.execute(create_table_logs)
        except Exception as e:
            print("Error in creating logs table")
            print(str(e))
            sleep(3)
            conn.rollback()

        #query to select data from database
        search_query = "SELECT * FROM logs WHERE username = ?"

        #tries to select data from database if error exists then catches it
        try:
            cr.execute(search_query, (self.username,))
            rec = cr.fetchall()     #fetching all the transactions of respective user
            print(tabulate(rec, headers=[ 'Username', 'Ammount', 'Date'], tablefmt='orgtbl'))   #printing trans in tabular manner
            print('"+" means ammount deposited and "-" means ammount withdrawn')
            input("Enter any word to Continue")
        except Exception as e:
            print("Error in checking transactions")
            print(str(e))
            conn.rollback()

        sleep(3)        #waiting for 3 secs
        conn.close()    #closing the database connection


    #Module for loan request by user
    def request_loan(self):
        amount = int(input("Enter the ammount you want to take as loan:     "))

        conn = sqlite3.connect("database.db")   #creating connectionto db
        cr = conn.cursor()  #cursor to db

        #creating table if it doesnot exists
        create_table_loan = """CREATE TABLE IF NOT EXISTS loans(
        loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        amount INTEGER NOT NULL,
        date_taken TEXT,
        due_date TEXT,
        next_due_date TEXT,
        interest REAL,
        emi REAL,
        loan_status INTEGER NOT NULL DEFAULT 0
        )"""
        #date_taken is from the date it is approved
        #1 in loan_status = approved, 0: not approved yet

        try: #build table
            cr.execute(create_table_loan)
        except Exception as e:
            print("Error in creating 'complaints' table")
            print(str(e))
            conn.rollback()

        fetch_id = "SELECT aid FROM accounts WHERE username = ?"
        ids = cr.execute(fetch_id,(self.username,))
        userid = cr.fetchone()[0]

        loan_requests = "INSERT INTO loans(user__id, amount) VALUES(?,?)" #query for adding loan request to db

        #tries to add loan request to database if error exists then catches it
        try:
            cr.execute(loan_requests, (userid, amount,))   #adding loan request with ammount
            print("Your loan request has been registered.")
        except Exception as e:
            print("Error in registering request")
            print(str(e))
            conn.rollback()

        sleep(3)        #waiting for 3 secs
        conn.commit()   #commiting the changes to database
        conn.close()    #closing the database connection


class AccountManagement:
    """docstring for AccountManagement"""
    def __init__(self, val):
        self.val = val
        if val == loan_acc:
            self.loan_accounts()
        else:
            self.daily_calculation()

    def loan_accounts(self):
        # print all loans active -  if u can think any thing more, add that too
        conn = sqlite3.connect("database.db")  #creating connection to db
        cr = conn.cursor()  #cursor to db

        #creating table if it doesnot exists
        create_table_loan = """CREATE TABLE IF NOT EXISTS loans(
        loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        amount INTEGER NOT NULL,
        date_taken TEXT,
        due_date TEXT,
        next_due_date TEXT,
        interest REAL,
        emi REAL,
        loan_status INTEGER NOT NULL DEFAULT 0
        )"""
        #date_taken is from the date it is approved
        #1 in loan_status = approved, 0: not approved yet
        try:    #build table
            cr.execute(create_table_loan)
        except Exception as e:
            print("Error in creating 'complaints' table")
            print(str(e))
            conn.rollback()

        search_query = "SELECT * FROM logs WHERE loan_status = ?"   #selecting only active loan users not loan requests

        #trying to select only active loan users not loan requests else catches error
        try:
            cr.execute(search_query, (1,))
            rec = cr.fetchall()
            print(tabulate(rec, headers=[ 'Username', 'Ammount', 'Starting Date', 'Ending Date', 'Next Due Date', 'Intrest Rates', 'EMI', 'Status'], tablefmt='orgtbl'))
            input("Enter any word to Continue: ")
        except Exception as e:
            print("Error in checking loan accounts")
        print(str(e))
        conn.rollback()

        sleep(3)        #waiting for 3 seconds
        conn.close()    #closing the db connection
        return


     # intrest rate and taxcalcualtion module
    def deposit_accounts(self):
        #calcluates intrest after deducting tax and make changes in database
        def interest_rates(self):
            #calculates tax on the intrest
            def tax_calculator(self, amount):
                tax = ammount * 10.0 #Given in question as 10%
                return tax

            #calcluates intrest after deducting tax
            def interest_calculator(self, amount, rate):
                # fetch rates from database for various deposits
                intrest = ammount * rate
                tax = self.taxCalculator(intrest, rate)
                totalAmmount = ammount + intrest - tax
                return totalAmmount

            conn = sqlite3.connect("database.db")       #connecting to db
            cr_rate = conn.cursor() #cursor  to db

            search_query = "SELECT rate_val FROM rates WHERE rate_name=?" #query to select savings rate from database
            try: #selecting savings rate from database
                cr_rate.execute(search_query, (savings,))
                rate_li = cr_rate.fetchall()
            except Exception as e:
                print("Error fetching intrest rates")
                print(str(e))
                conn.rollback()

            rate = rate_li[0] / 365 #converting annualy intrest to  daily intrest

            cr = conn.cursor()  #cursor to db
            #create table if it doesnt exist
            create_table_deposits = """CREATE TABLE IF NOT EXISTS deposits(
            deposit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            amount INTEGER NOT NULL,
            cumlative REAL DEFAULT 0,
            )"""
            try: # build table
                cr.execute(create_table_deposits)
            except Exception as e:
                print("Error in creating deposits table")
                print(str(e))
                sleep(3)
                conn.rollback()

            search_query = "SELECT username, amount, cumlative FROM deposits"   #query to select username, ammount and prev daily intrest of all users
            try:    #executing the above query
                cr.execute(search_query)
                rec = cr.fetchall()
            except Exception as e:
                print("Error in checking transactions")
                print(str(e))
                conn.rollback()

            #calculating daily intrests for all and adding it to db
            for i in rec:
                cuml = interest_calculator(i[1], rate) + i[2]   #summation of previous and current daily intrest
                cur = conn.cursor()

                query = "UPDATE deposits SET cumlative = ? WHERE username = ?"  #query to save daily intrest to database

                try:    #executing above query
                    cur.execute(query, (cuml, i[0],))
                except Exception as e:
                    print("Error while Updating Daily Intrest")
                    print(str(e))
                    conn.rollback()

                conn.commit() #commiting the changes
            conn.close()    #closing the connection

        conn = sqlite3.connect("database.db")   #creating connection to db
        cr = conn.cursor()  #cursor t db


    def daily_calculation(self):
        #creating date table if it doesnot exists
        create_table_date = """CREATE TABLE IF NOT EXISTS dates(
        deposit_id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT
        )"""

        try: # build table
            cr.execute(create_table_date)
        except Exception as e:
            print("Error in creating datetable")
            print(str(e))
            conn.rollback()

        query = "SELECT date FROM dates"    #selecting all dates from table date
        try:    #ececuting above query
            cr.execute(query)
            rec = cr.fetchall()
        except Exception as e:
            print("Error in getching dates")
            print(str(e))
            conn.rollback()

        l = len(rec)    #total entires if date
        #if no entry in date or last entry of date table is different from current date, then only calculates daily intrest for them
        if l == 0 or rec[-1] != str(date.today()):
            self.deposit_accounts(self)  # function to calculate daily intresst for all
            query = "INSERT into dates(date) VALUES(?)" #query to select all the dates
            try:    #executingabove query
                cr.execute(query, (str(date.today()),))
                l += 1
            except Exception as e:
                print("Error in adding to dates")
                print(str(e))
                conn.rollback()
            conn.commit()   #commiting changes to db
        # Adding intrest at the end of month
        if l % 30 == 0:
            cr = conn.cursor()  #cursor to db
            search_query = "SELECT username, amount, cumlative FROM deposits"   #search query to selsct data
            try:    #executing above query
                cr.execute(search_query)
                rec = cr.fetchall()
            except Exception as e:
                print("Error in updating balance with intrest")
                print(str(e))
                conn.rollback()

            #adding intrest to main balance and making daily intrest 0
            for i in rec:
                bal = i[1] + i[2]
                query = "UPDATE deposits SET cumlative = 0, amount = ? WHERE username = ?"  #query to add intrest to main balance and making daily intrest 0
                try:    #executing above query
                    cur.execute(query, (bal, i[0],))
                except Exception as e:
                    print("Error while Updating Monthly Intrest")
                    print(str(e))
                    conn.rollback()

                conn.commit()   #commiting the changes
        conn.close()    #closing connection to database









if __name__ == '__main__':
    print('Interest Added, login screen')
    sys_ser = SystemServices()
    status = False
    user_cat = ''
    while status == False: # WHILE NOT SUCCESSULLY LOGGED IN REPEAT
        status, user_cat = sys_ser.login()
    if user_cat == 'admin':
        admin = Admin()
    else:
        client = Client_Interface(user_cat)
