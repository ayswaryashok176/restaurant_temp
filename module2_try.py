import sqlite3
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from tkinter import *
from tkinter import messagebox
nltk.download('stopwords')

dataset = pd.read_csv('Restaurant_Reviews.tsv',delimiter='\t', quoting=3)
corpus = []
rras_code = "minor"
food_rev = {}
food_perc = {}

conn = sqlite3.connect(r"C:\Users\ayswa\OneDrive\Desktop\Minor project\Restaurant_food_data.db")
c = conn.cursor()
conn.close()

for i in range(0, 1000):
	review = re.sub('[^a-zA-Z]', ' ', dataset['Review'][i])
	review = review.lower()
	review = review.split()
	ps = PorterStemmer()
	all_stopwords = stopwords.words('english')
	all_stopwords.remove('not')
	review = [ps.stem(word)for word in review if not word in set(all_stopwords)]
	review = ' '.join(review)
	corpus.append(review)

cv = CountVectorizer(max_features=1500)
X = cv.fit_transform(corpus).toarray()
y = dataset.iloc[:, -1].values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=0)

classifier = GaussianNB()
classifier.fit(X_train, y_train)
y_pred = classifier.predict(X_test)

variables = []
clr_variables = []

foods = ["Idly", "Dosa", "Vada", "Roti", "Meals", "Veg Biryani","Egg Biryani", "Chicken Biryani", "Mutton Biryani",
		"Ice Cream", "Noodles", "Manchooriya", "Orange juice","Apple Juice", "Pineapple juice", "Banana juice"]

for i in foods:
	food_rev[i] = []
	food_perc[i] = [0.0, 0.0]

def estimate(s):

	conn = sqlite3.connect(r"C:\Users\ayswa\OneDrive\Desktop\Minor project\Restaurant_food_data.db")
	c = conn.cursor()
	review = re.sub('[^a-zA-Z]', ' ', s)
	review = review.lower()
	review = review.split()
	ps = PorterStemmer()
	all_stopwords = stopwords.words('english')
	all_stopwords.remove('not')
	
	review = [ps.stem(word)for word in review if not word in set(all_stopwords)]
	review = ' '.join(review)
	X = cv.transform([review]).toarray()
	res = classifier.predict(X) # list
	
	if "not" in review:
		res[0] = abs(res[0]-1)
	
	selected_foods = []
	for i in range(len(foods)):
		if variables[i].get() == 1:
			selected_foods.append(foods[i])
	
	c.execute("SELECT *,oid FROM item")
	records = c.fetchall()
	
	for i in records:
		rec = list(i)
		if rec[0] in selected_foods:
			n_cust = int(rec[1])+1
			n_pos = int(rec[2])
			n_neg = int(rec[3])
			
			if res[0] == 1:
				n_pos += 1
			else:
				n_neg += 1
				
			pos_percent = round((n_pos/n_cust)*100, 1)
			neg_percent = round((n_neg/n_cust)*100, 1)
			c.execute('''UPDATE item SET Item_name=:item_name,No_of_customers\
			=:no_of_customers,No_of_positive_reviews=:no_of_positives,\
			No_of_negative_reviews=:no_of_negatives,Positive_percentage\
			=:pos_perc,Negative_percentage=:neg_perc where oid=:Oid''',
					{
						'item_name': rec[0],
						'no_of_customers': str(n_cust),
						'no_of_positives': str(n_pos),
						'no_of_negatives': str(n_neg),
						'pos_perc': str(pos_percent)+"%",
						'neg_perc': str(neg_percent)+"%",
						'Oid': foods.index(rec[0])+1
					}
					)
	selected_foods = []

	conn.commit()
	conn.close()
	
def take_review():
	root2 = Toplevel()
	root2.title(main+"give review")

	label = Label(root2, text="RESTAURANT REVIEW ANALYSIS SYSTEM",
				bd=2, font=('Arial', 47, 'bold', 'underline'))

	req1 = Label(root2, text="Select the item(s) you have taken.....")

	conn = sqlite3.connect(r"C:\Users\ayswa\OneDrive\Desktop\Minor project\Restaurant_food_data.db")
	c = conn.cursor()

	chk_btns = []
	selected_foods = []
	req2 = Label(root2, text="Give your review below....")
	rev_tf = Entry(root2, width=125, borderwidth=5)
	req3 = Label(root2, text="NOTE : Use not instead of n't.")
	global variables
	variables = []
	chk_btns = []

	for i in range(len(foods)):
		var = IntVar()
		chk = Checkbutton(root2, text=foods[i], variable=var)
		variables.append(var)
		chk_btns.append(chk)

	label.grid(row=0, column=0, columnspan=4)
	req1.grid(row=1, column=0, columnspan=4, sticky=W+E)
	req1.config(font=("Helvetica", 30))

	for i in range(4):
		for j in range(4):
			c = chk_btns[i*4+j]
			c.grid(row=i+3, column=j, columnspan=1, sticky=W)
	selected_foods = []

	submit_review = Button(root2, text="Submit Review", font=(
		'Arial', 20), padx=100, pady=20, command=lambda: [
		estimate(rev_tf.get()), root2.destroy()])

	root2.attributes("-fullscreen", True)
	req2.grid(row=7, column=0, columnspan=4, sticky=W+E)
	req2.config(font=("Helvetica", 20))
	rev_tf.grid(row=8, column=1, rowspan=3, columnspan=2, sticky=S)
	req3.grid(row=11, column=1, columnspan=2)
	submit_review.grid(row=12, column=0, columnspan=4)
	conn.commit()
	conn.close()
def access_data():
	root5 = Toplevel()
	root5.title(main+"Restaurant_Database")
	
	label = Label(root5, text="RESTAURANT REVIEW ANALYSIS SYSTEM",
				bd=2, font=('Arial', 47, 'bold', 'underline'))
	
	title1 = Label(root5, text="S.NO", font=('Arial', 10, 'bold', 'underline'))
	
	title2 = Label(root5, text="FOOD ITEM", font=(
		'Arial', 10, 'bold', 'underline'))
	
	title3 = Label(root5, text="NO.OF CUSTOMERS",
				font=('Arial', 10, 'bold', 'underline'))
	
	title4 = Label(root5, text="NO.OF POSITIVE REVIEWS",
				font=('Arial', 10, 'bold', 'underline'))
	
	title5 = Label(root5, text="NO.OF NEGATIVE REVIEWS",
				font=('Arial', 10, 'bold', 'underline'))
	
	title6 = Label(root5, text="POSITIVE RATE",
				font=('Arial', 10, 'bold', 'underline'))
	
	title7 = Label(root5, text="NEGATIVE RATE",
				font=('Arial', 10, 'bold', 'underline'))

	label.grid(row=0, column=0, columnspan=7)
	title1.grid(row=1, column=0)
	title2.grid(row=1, column=1)
	title3.grid(row=1, column=2)
	title4.grid(row=1, column=3)
	title5.grid(row=1, column=4)
	title6.grid(row=1, column=5)
	title7.grid(row=1, column=6)

	conn = sqlite3.connect(r"C:\Users\ayswa\OneDrive\Desktop\Minor project\Restaurant_food_data.db")
	c = conn.cursor()

	c.execute("SELECT *,oid from item")
	records = c.fetchall()
	pos_rates = []

	for record in records:
		record = list(record)
		pos_rates.append(float(record[-3][:-1]))

	max_pos = max(pos_rates)
	min_pos = min(pos_rates)

	for i in range(len(records)):
		rec_list = list(records[i])
		if str(max_pos)+"%" == rec_list[-3]:
			rec_lab = [Label(root5, text=str(rec_list[-1]), fg="green")]
			for item in rec_list[:-1]:
				lab = Label(root5, text=item, fg="green")
				rec_lab.append(lab)
		elif str(min_pos)+"%" == rec_list[-3]:
			rec_lab = [Label(root5, text=str(rec_list[-1]), fg="red")]
			for item in rec_list[:-1]:
				lab = Label(root5, text=item, fg="red")
				rec_lab.append(lab)
		else:
			rec_lab = [Label(root5, text=str(rec_list[-1]))]
			for item in rec_list[:-1]:
				lab = Label(root5, text=item)
				rec_lab.append(lab)

		for j in range(len(rec_lab)):
			rec_lab[j].grid(row=i+2, column=j)

	exit_btn = Button(root5, text="Exit", command=root5.destroy)
	exit_btn.grid(row=len(records)+5, column=3)

	conn.commit()
	conn.close()
	root5.attributes("-fullscreen", True)
def clr_itemdata():
	root6 = Toplevel()
	root6.title(main+"clear_item_data")
	
	label = Label(root6, text="RESTAURANT REVIEW ANALYSIS SYSTEM",
				bd=2, font=('Arial', 47, 'bold', 'underline'))
	
	req1 = Label(root6, text="Pick the items to clear their corresponding\
	item data....")
	
	chk_list = []
	global clr_variables
	clr_variables = []
	
	for i in range(len(foods)):
		var = IntVar()
		chk = Checkbutton(root6, text=foods[i], variable=var)
		clr_variables.append(var)
		chk_list.append(chk)
	
	label.grid(row=0, column=0, columnspan=4)
	req1.grid(row=1, column=0, columnspan=4, sticky=W+E)
	req1.config(font=("Helvetica", 30))
	
	for i in range(4):
		for j in range(4):
			c = chk_list[i*4+j]
			c.grid(row=i+3, column=j, columnspan=1, sticky=W)
	
	clr_item = Button(root6, text="Clear", font=(
		'Arial', 20), padx=100, pady=20, command=lambda: [
	clr_data(), root6.destroy()])
	
	clr_item.grid(row=8, column=0, columnspan=4)
	root6.attributes("-zoomed", True)



def clr_alldata(foods):
    # Confirm the action from the user
    confirm = messagebox.askquestion(
        "Confirmation", "Are you sure to delete all data?")
    
    if confirm == "yes":
        # Connect to the database
        conn = sqlite3.connect(r"C:\Users\ayswa\OneDrive\Desktop\Minor project\Restaurant_food_data.db")
        c = conn.cursor()

        # Fetch all row OIDs to ensure correct updates
        c.execute("SELECT oid FROM item")
        oids = c.fetchall()

        # Iterate over the items and reset the values
        for i in range(len(foods)):
            if i < len(oids):  # Ensure we don't exceed the number of rows in the table
                c.execute("""
                    UPDATE item
                    SET item_name = :item_name,
                        no_of_customers = :no_of_customers,
                        no_of_positives = :no_of_positives,
                        no_of_negatives = :no_of_negatives,
                        pos_perc = :pos_perc,
                        neg_perc = :neg_perc
                    WHERE oid = :Oid""",
                    {
                        'item_name': foods[i],
                        'no_of_customers': 0,  # Integer values
                        'no_of_positives': 0,  # Integer values
                        'no_of_negatives': 0,  # Integer values
                        'pos_perc': "0.0%",    # String for percentage
                        'neg_perc': "0.0%",    # String for percentage
                        'Oid': oids[i][0]      # Fetch the correct OID from the database
                    }
                )

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

def popup():
	messagebox.showerror("Error Message!", "Incorrect code!")


def clr_data(foods, clr_variables):
    # Connect to the SQLite database
    conn = sqlite3.connect(r"C:\Users\ayswa\OneDrive\Desktop\Minor project\Restaurant_food_data.db")
    c = conn.cursor()

    # Iterate through the food items and clear data for selected ones
    for i in range(len(foods)):
        if clr_variables[i].get() == 1:  # Check if the item is selected
            c.execute("""
                UPDATE item
                SET no_of_customers = 0, 
                    no_of_positive_reviews = 0, 
                    no_of_negative_reviews = 0, 
                    positive_percentage = 0.0, 
                    negative_percentage = 0.0 
                WHERE item_name = :item_name
            """, {'item_name': foods[i]})

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    # Show a confirmation message
    messagebox.showinfo("Clear Data", "Selected item data has been cleared.")

	
def view_details(s):
	if(s != rras_code):
		popup()
	else:
		root4 = Toplevel()
		root4.title(main+"view_details")
		label = Label(root4, text="RESTAURANT REVIEW ANALYSIS SYSTEM",
					bd=2, font=('Arial', 47, 'bold', 'underline'))
		sug1 = Label(
			root4, text="Click to view the data from your database....")
		
		acc_btn = Button(root4, text="View Data", font=(
			'Arial', 20), padx=100, pady=10, command=access_data)
		
		sug2 = Label(root4, text="Click to clear specific item data...")
		
		itemclr_btn = Button(root4, text="Clear Item Data", font=(
			'Arial', 20), padx=100, pady=10, command=clr_itemdata)
		
		sug3 = Label(root4, text="Click the below buttonto clear all item data...")
		
		allclr_btn = Button(root4, text="Clear All Data", font=(
			'Arial', 20), padx=100, pady=10, command=clr_alldata)
		
		exit_btn = Button(root4, text="Exit", font=(
			'Arial', 20), padx=100, pady=10, command=root4.destroy)

		root4.attributes("-fullscreen", True)
		label.grid(row=0, column=0)
		sug1.grid(row=1, column=0)
		sug1.config(font=("Helvetica", 30))
		acc_btn.grid(row=3, column=0)
		sug2.grid(row=4, column=0)
		sug2.config(font=("Helvetica", 30))
		itemclr_btn.grid(row=6, column=0)
		sug3.grid(row=7, column=0)
		sug3.config(font=("Helvetica", 30))
		allclr_btn.grid(row=8, column=0)
		exit_btn.grid(row=20, column=0, sticky=S)

def login():
	root3 = Toplevel()
	root3.title(main+"owner verification")
	
	label = Label(root3, text="RESTAURANT REVIEW ANALYSIS SYSTEM",bd=2, font=('Arial', 47, 'bold', 'underline'))
	
	label2 = Label(root3, text="VERIFY OWNERSHIP", bd=1,font=('Helvetica', 30, 'bold', 'underline'))
	
	label3 = Label(root3, text="To verify your ownership, please \enter your restaurant's private rras code....",bd=1, font=('Helvetica', 20, 'bold'))
	ent = Entry(root3, show="*", borderwidth=2)
	submit_code = Button(root3, text="Submit", font=('Arial', 20), padx=80,pady=20, command=lambda: [view_details(ent.get()), root3.destroy()])
	
	root3.attributes("-fullscreen", True)
	label.grid(row=0, column=0, columnspan=3)
	label2.grid(row=1, column=0, sticky=W+E, columnspan=3)
	label3.grid(row=2, column=0, sticky=W, columnspan=3)
	ent.grid(row=3, column=1, columnspan=1)
	submit_code.grid(row=4, column=1, columnspan=1)
	
import sqlite3

def init_data(foods):
    # Connect to the database
    conn = sqlite3.connect(r"C:\Users\ayswa\OneDrive\Desktop\Minor project\Restaurant_food_data.db")
    c = conn.cursor()

    # Create the table if it does not exist
    c.execute('''CREATE TABLE IF NOT EXISTS item (
                    item_name TEXT,
                    no_of_customers INTEGER,
                    no_of_positives INTEGER,
                    no_of_negatives INTEGER,
                    pos_perc TEXT,
                    neg_perc TEXT
                )''')

    # Insert data into the table
for i in range(len(foods)):
		c.execute("""
		INSERT INTO item (item_name, no_of_customers, no_of_positives, no_of_negatives, pos_perc, neg_perc)
		VALUES (:item_name, :no_of_customers, :no_of_positives, :no_of_negatives, :pos_perc, :neg_perc)""",
		{
			'item_name': foods[i],
			'no_of_customers': 0,
			'no_of_positives': 0,
			'no_of_negatives': 0,
			'pos_perc': "0.0%",  # This is fine if you prefer it as a string
			'neg_perc': "0.0%"   # This is fine if you prefer it as a string
		}
	)
		
conn.commit()
conn.close()


	


    # Commit the changes and close the connection
    #conn.commit()
    #conn.close()

root1 = Tk()
main = "Restaurant Review Analysis System/"
root1.title(main+"Welcome Page")

label = Label(root1, text="RESTAURANT REVIEW ANALYSIS SYSTEM",bd=2, font=('Arial', 47, 'bold', 'underline'))

ques = Label(root1, text="Are you a Customer or Owner ???")

cust = Button(root1, text="Customer", font=('Arial', 20),padx=80, pady=20, command=take_review)

owner = Button(root1, text="Owner", font=('Arial', 20),padx=100, pady=20, command=login)
#c.execute("DELETE FROM item")
root1.attributes("-fullscreen", True)
label.grid(row=0, column=0)
ques.grid(row=1, column=0, sticky=W+N+S+E)
ques.config(font=("Helvetica", 30))
cust.grid(row=2, column=0)
owner.grid(row=3, column=0)
root1.mainloop()







	










