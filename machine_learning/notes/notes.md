# CanYouCatchIt?
A web application allowing you to obtain the percentage of chance that your bus/tram/metro is late. 💻🤖🎲🚌 🚎🚇🔮

_Build with the STIB API (available [here](https://opendata.stib-mivb.be/store/))_

# Notes: Making some models 💻🤖🚌 🚎🚇
Here we are to make some machine learning models

## Look at the Big Picture

### Frame the problem
We want to use this model to predict the stib vehicule delay acording to the time and weather.

It's clearly a supervised learning task since we have labeled trainning examples (for each instance we have an excepted output). It's also a regression task, since we are asked to predict a value. More specifically, this is a multivariate regression problem because the system use multiple features to make a prediction. Firstly we are going to use batch learning (for now the data is small enough to fit in memory) event if it's not telored for realtime data. In the second time, we will try to implement a online learning system that can learn about new data on the fly.
If we don't achieve a significant precision, we can change the project into a classification one. In this case, getting the delay perfectly right is not important at all; your system just needs to get the category right (e.g., "Significant Early", "Early", "On time", "Delay", or "Significant Delay").

### Select a Performance Measure

A typical performance measure for regression problems is the Root Mean Square Error (RMSE). It measures the standard deviation of the errors the system makes in its predictions.

### Get the data
#### Create the Workspace
``` pip3 install --upgrade jupyter matplotlib numpy pandas scipy scikit-learn ```


<!-- But what if the downstream system actually converts the prices into categories (e.g., “cheap,”
“medium,” or “expensive”) and then uses those categories instead of the prices them
selves? In this case, getting the price perfectly right is not important at all; your sys‐
tem just needs to get the category right. If that’s so, then the problem should have
been framed as a classification task, not a regression task. You don’t want to find this
out after working on a regression system for months.
Fortunately, after talking with the team in charge of the downstream system, you are
confident that they do indeed need the actual prices, not just categories. Great! You’re
all set, the lights are green, and you can start coding now!

Supervised learning
In supervised learning, the training data you feed to the algorithm includes the desired solutions, called labels (Figure 1-5).
A typical supervised learning task is classification. The spam filter is a good example of this: it is trained with many example emails along with their class (spam or ham), and it must learn how to classify new emails.
Another typical task is to predict a target numeric value, such as the price of a car, given a set of features (mileage, age, brand, etc.) called predictors.
This sort of task is called regression (Figure 1-6). 1 To train the system, you need to give it many examples of cars, including both their predictors and their labels (i.e., their prices). -->