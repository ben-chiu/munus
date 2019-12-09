# munus
CS50 Project for Ben Chiu and Nick Lauer

Summary: The website, called munus or Latin for “exchange”, allows students in the Harvard Yard to make pickup requests to select stores in the Square. They can decide how much they are willing to pay for such a delivery. At the same time, any user can view all open orders and fulfill any of the pickups. When an order is fulfilled, the deliverer gets the cost of the project plus the delivery fee added to their account. Finally, users can cash out their account, although this functionality is impossible without officially registering a business and bank account with Stripe, so we have implemented a simulation instead.

Usage:
Download the repository and follow the installation steps 

Upon registering with an email address, password, and room number, you are directed to add money to your account using Stripe. If you want to make orders, you will need to continue through this form. To only fulfill pickups, you can click on “Pickups” in the navigation bar.

After adding money to your account, you can navigate to the catalogue either from the nav bar or by following the link on the successful payment page. The catalogue contains links to thousands of products from a variety of stores, almost all of which were scraped from the CVS catalogue. There’s a search bar, which uses SQL to filter on the products that you see. Each product in the table is a hyperlink to the order page for that product.

On the order form, you can choose how many of the product you want, how much you want to pay the deliverer, and when the order should expire. You can also cancel orders from the upper right user menu. 

If you instead want to pick up orders, you can navigate over to the pickup page. Here, you can see a list of all open orders besides your own, listed in descending order of delivery fee. If you only want to deliver to a certain yard to minimize walking, you can filter based on store. If you are in a certain store and only want to check open orders there, you can filter on store as well. Finally, you can pick up an order by clicking the “pick up” link, which closes the order, adds it to your transaction history, and adds the correct amount to your current balance.

Other functionality can be found in the user menu, which can be found by clicking on the user icon in the right side of the nav bar. You can change your password, see your transaction history, log out, or even empty your account. Note: it is impossible to be compensated by munus since we have not established a bank account for the Stripe payment system. Instead, following that branch of the navigation bar will show the user a representation of how the real process would look.

Installation Steps (assumes the user has Atom):
1. Download the repository and unzip it.
2. The project requires many libraries that may not be downloaded by the user. These are installed in the console using “pip install” + libraryName. These are:
    1. stripe
    2. sqlite3
    3. flask
    4. flask_session
3. The project can be run with “flask run” in the console and is located at a URL that is given upon submitting that command.
