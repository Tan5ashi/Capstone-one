#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import scipy
import matplotlib.pyplot as plt
from sklearn import tree
from IPython.display import Image
get_ipython().run_line_magic('matplotlib', 'inline')
from sklearn import preprocessing
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc, ConfusionMatrixDisplay, RocCurveDisplay


# ### Gradient boosting
# 
# You may recall that we last encountered gradients when discussing the gradient descent algorithm in the context of fitting linear regression models.  For a particular regression model with n parameters, an n+1 dimensional space existed defined by all the parameters plus the cost/loss function to minimize.  The combination of parameters and loss function define a surface within the space.  The regression model is fitted by moving down the steepest 'downhill' gradient until we reach the lowest point of the surface, where all possible gradients are 'uphill.'  The final model is made up of the parameter estimates that define that location on the surface.
# 
# Throughout all iterations of the gradient descent algorithm for linear regression, one thing remains constant: The underlying data used to estimate the parameters and calculate the loss function never changes.  In gradient boosting, however, the underlying data do change.  
# 
# Each time we run a decision tree, we extract the residuals.  Then we run a new decision tree, using those residuals as the outcome to be predicted.  After reaching a stopping point, we add together the predicted values from all of the decision trees to create the final gradient boosted prediction.
# 
# Gradient boosting can work on any combination of loss function and model type, as long as we can calculate the derivatives of the loss function with respect to the model parameters.  Most often, however, gradient boosting uses decision trees, and minimizes either the  residual (regression trees) or the negative log-likelihood (classification trees).  
# 
# Let’s go through a simple regression example using Decision Trees as the base predictors (of course Gradient Boosting also works great with regression tasks). This is called Gradient Tree Boosting, or Gradient Boosted Regression Trees. First, let’s fit a `DecisionTreeRegressor` to the training set.

# In[2]:


np.random.seed(42)
X = np.random.rand(100, 1) - 0.5
y = 3*X[:, 0]**2 + 0.05 * np.random.randn(100)


# In[3]:


plt.plot(X,y,'k.')

plt.show()


# In[4]:


from sklearn.tree import DecisionTreeRegressor

tree_reg1 = DecisionTreeRegressor(max_depth=2, random_state=42)
tree_reg1.fit(X, y)


# Now train a second `DecisionTreeRegressor` on the residual errors made by the first predictor:

# In[5]:


y2 = y - tree_reg1.predict(X)
tree_reg2 = DecisionTreeRegressor(max_depth=2, random_state=42)
tree_reg2.fit(X, y2)


# Then we train a third regressor on the residual errors made by the second predictor:
# 
# 

# In[6]:


y3 = y2 - tree_reg2.predict(X)
tree_reg3 = DecisionTreeRegressor(max_depth=2, random_state=42)
tree_reg3.fit(X, y3)


# In[7]:


plt.plot(X,y2,'r.')
plt.plot(X,y3,'.', c='orange')


# Now we have an ensemble containing three trees. It can make predictions on a new instance simply by adding up the predictions of all the trees:

# In[8]:


X_new = np.array([[0.8]])


# In[9]:


y_pred = [tree.predict(X_new) for tree in (tree_reg1, tree_reg2, tree_reg3)]


# In[10]:


y_pred


# In[11]:


y_pred = sum(y_pred)
y_pred


# The figure below represents the predictions of these three trees in the left column, and the ensemble’s predictions in the right column. In the first row, the ensemble has just one tree, so its predictions are exactly the same as the first tree’s predictions. In the second row, a new tree is trained on the residual errors of the first tree. On the right you can see that the ensemble’s predictions are equal to the sum of the predictions of the first two trees. Similarly, in the third row another tree is trained on the residual errors of the second tree. You can see that the ensemble’s predictions gradually get better as trees are added to the ensemble.

# **<font color='teal'>Run the below cell to develop a visual representation.</font>**

# In[12]:


def plot_predictions(regressors, X, y, axes, label=None, style="r-", data_style="b.", data_label=None):
    x1 = np.linspace(axes[0], axes[1], 500)
    y_pred = sum(regressor.predict(x1.reshape(-1, 1)) for regressor in regressors)
    plt.plot(X[:, 0], y, data_style, label=data_label)
    plt.plot(x1, y_pred, style, linewidth=2, label=label)
    if label or data_label:
        plt.legend(loc="upper center", fontsize=16)
    plt.axis(axes)

plt.figure(figsize=(11,11))

plt.subplot(321)
plot_predictions([tree_reg1], X, y, axes=[-0.5, 0.5, -0.1, 0.8], label="$h_1(x_1)$", style="g-", data_label="Training set")
plt.ylabel("$y$", fontsize=16, rotation=0)
plt.title("Residuals and tree predictions", fontsize=16)

plt.subplot(322)
plot_predictions([tree_reg1], X, y, axes=[-0.5, 0.5, -0.1, 0.8], label="$h(x_1) = h_1(x_1)$", data_label="Training set")
plt.ylabel("$y$", fontsize=16, rotation=0)
plt.title("Ensemble predictions", fontsize=16)

plt.subplot(323)
plot_predictions([tree_reg2], X, y2, axes=[-0.5, 0.5, -0.5, 0.5], label="$h_2(x_1)$", style="g-", data_style="k+", data_label="Residuals")
plt.ylabel("$y - h_1(x_1)$", fontsize=16)

plt.subplot(324)
plot_predictions([tree_reg1, tree_reg2], X, y, axes=[-0.5, 0.5, -0.1, 0.8], label="$h(x_1) = h_1(x_1) + h_2(x_1)$")
plt.ylabel("$y$", fontsize=16, rotation=0)

plt.subplot(325)
plot_predictions([tree_reg3], X, y3, axes=[-0.5, 0.5, -0.5, 0.5], label="$h_3(x_1)$", style="g-", data_style="k+")
plt.ylabel("$y - h_1(x_1) - h_2(x_1)$", fontsize=16)
plt.xlabel("$x_1$", fontsize=16)

plt.subplot(326)
plot_predictions([tree_reg1, tree_reg2, tree_reg3], X, y, axes=[-0.5, 0.5, -0.1, 0.8], label="$h(x_1) = h_1(x_1) + h_2(x_1) + h_3(x_1)$")
plt.xlabel("$x_1$", fontsize=16)
plt.ylabel("$y$", fontsize=16, rotation=0)

plt.savefig("gradient_boosting_plot.png")
plt.show()


# Now that you have solid understanding of Gradient Boosting in the regression scenario, let's apply the same algorithm to a classification problem. Specifically, the Titanic dataset and predicting survival.

# **<font color='teal'>Use pandas read csv to load in the Titantic data set into a dataframe called df.</font>**
# 
# Hint: in this case you can use [dropna()](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.dropna.html) to just throw away any incomplete rows. For the purpose of this exercise we will disregard them but obviously in the real world you need to be much more careful and decide how to handle incomplete observations. 

# In[2]:


df = pd.read_csv('titanic.csv')
df.dropna(inplace=True)
df.head()


# In[3]:


df.convert_dtypes().dtypes


# In[4]:


df.dtypes


# **<font color='teal'>Print the levels of the categorical data using 'select_dtypes'. </font>**

# In[5]:


df.select_dtypes(include='object').head()


# In[6]:


dfo = df.select_dtypes(include=['object'], exclude=['datetime'])
dfo.shape
#get levels for all variables
vn = pd.DataFrame(dfo.nunique()).reset_index()
vn.columns = ['VarName', 'LevelsCount']
vn.sort_values(by='LevelsCount', ascending =False)
vn


# In[24]:


df['Cabin'].unique()


# ***Dropping+Ignoring `Cabin`,`Name`,`Ticket` categorical features to streamline demonstration***

# **<font color='teal'>Create dummy features for the categorical features and add those to the 'df' dataframe. Make sure to also remove the original categorical columns from the dataframe.</font>**

# In[7]:


dft = pd.DataFrame(df.drop(df.columns,axis =1)).merge(pd.get_dummies(df.drop(['Name','Cabin','Ticket'],axis =1)),left_index=True,right_index=True).drop(['PassengerId'],axis =1)
print(dft.shape)
dft.head()


# **<font color='teal'>Print the null values for each column in the dataframe.</font>**

# In[8]:


dft.isna().sum()


# In[9]:


df = dft.copy()


# In[10]:


df.describe().T


# **<font color='teal'>Create the X and y matrices from the dataframe, where y = df.Survived </font>**

# In[12]:


X = df.drop(columns=['Survived'])
y = df['Survived']


# In[13]:


binary_columns = X.columns[X.columns.str.find('_')>0]


# In[14]:


scale_columns = X.columns[X.columns.str.find('_')<0]


# In[15]:


binary_columns


# In[16]:


scale_columns


# In[17]:


X.shape, y.shape


# In[39]:


X.head()


# **<font color='teal'>Apply the standard scaler to the X matrix.</font>**

# In[34]:


scaler = preprocessing.StandardScaler().fit(X)
X_scaled = scaler.transform(X)
X_scaled = pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
X_scaled.head()


# *do not scale encoded data?*

# In[23]:


X_scaled = preprocessing.StandardScaler().fit_transform(X[scale_columns])
X_scaled = pd.DataFrame(X_scaled, columns=scale_columns, index=X.index)
X_scaled.head()


# In[24]:


X_scaled = pd.concat([X_scaled, X[binary_columns]], axis=1)


# In[25]:


X_scaled.head()


# In[26]:


X_scaled.shape


# **<font color='teal'>Split the X_scaled and y into 75/25 training and testing data subsets..</font>**

# In[19]:


from sklearn.model_selection import train_test_split


# In[35]:


X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.25)


# **<font color='teal'>Run the cell below to test multiple learning rates in your gradient boosting classifier.</font>**

# In[21]:


print('scaled all data')
learning_rates = [0.05, 0.1, 0.25, 0.5, 0.75, 1]
results = pd.DataFrame()
for learning_rate in learning_rates:
    gb = GradientBoostingClassifier(n_estimators=20, learning_rate = learning_rate, max_features=2, max_depth = 2, random_state = 0)
    gb.fit(X_train, y_train)
    print("Learning rate: ", learning_rate)
    print("Accuracy score (training): {0:.3f}".format(gb.score(X_train, y_train)))
    print("Accuracy score (validation): {0:.3f}".format(gb.score(X_test, y_test)))
    results.loc[learning_rate,'Accuracy_Training'] = gb.score(X_train, y_train)
    results.loc[learning_rate,'Accuracy_Testing'] = gb.score(X_test, y_test)
    print()


# In[22]:


results.sort_values('Accuracy_Testing', ascending=False)


# **Did not scale binary features**

# In[28]:


print('did NOT scale encoded features')
learning_rates = [0.05, 0.1, 0.25, 0.5, 0.75, 1]
results = pd.DataFrame()
for learning_rate in learning_rates:
    gb = GradientBoostingClassifier(n_estimators=20, learning_rate = learning_rate, max_features=2, max_depth = 2, random_state = 0)
    gb.fit(X_train, y_train)
    print("Learning rate: ", learning_rate)
    print("Accuracy score (training): {0:.3f}".format(gb.score(X_train, y_train)))
    print("Accuracy score (validation): {0:.3f}".format(gb.score(X_test, y_test)))
    results.loc[learning_rate,'Accuracy_Training'] = gb.score(X_train, y_train)
    results.loc[learning_rate,'Accuracy_Testing'] = gb.score(X_test, y_test)
    print()


# In[29]:


results.sort_values('Accuracy_Testing', ascending=False)


# **<font color='teal'>Apply the best learning rate to the model fit and predict on the testing set. Print out the confusion matrix and the classification report to review the model performance.</font>**

# **Learning Rate: 0.10**
# 
# Best testing accuracy, answers seem to vary

# In[37]:


gb_answer = GradientBoostingClassifier(n_estimators=20, learning_rate = 0.1, max_features=2, max_depth = 2, random_state = 0)
gb_answer.fit(X_train, y_train)
y_pred = gb_answer.predict(X_scaled)
gb_answer.score(X_test, y_test)


# In[38]:


cm = confusion_matrix(y, y_pred)
cm


# In[39]:


disp = ConfusionMatrixDisplay(cm, display_labels=['Survived', 'Died'])
disp.plot()
plt.text(1,0.1,'false negatives', color='y', ha='center', fontweight='bold')
plt.text(0,1.1,'false positives', color='y', ha='center', fontweight='bold')

plt.text(0,0.1,'correct postive', color='g', ha='center', fontweight='bold')
plt.text(1,1.1,'correct negative', color='g', ha='center', fontweight='bold')

plt.show()


# In[40]:


print(classification_report(y, y_pred))


# **<font color='teal'>Calculate the ROC for the model as well.</font>**

# In[41]:


fpr, tpr, thresholds = roc_curve(y, y_pred)
roc_auc = auc(fpr, tpr)
display = RocCurveDisplay(fpr=fpr, tpr=tpr, roc_auc=roc_auc)
display.plot()
plt.text(0.5, 0.5, f'AUC: {round(roc_auc,3)}', fontweight='bold')
plt.legend([])
plt.show()


# In[ ]:





# In[ ]:





# ## Learning Rate: 0.05
# *worse performance with this split*

# In[42]:


gb_answer = GradientBoostingClassifier(n_estimators=20, learning_rate = 0.05, max_features=2, max_depth = 2, random_state = 0)
gb_answer.fit(X_train, y_train)
y_pred = gb_answer.predict(X_scaled)
print('Test Accuracy\n',gb_answer.score(X_test, y_test))

cm = confusion_matrix(y, y_pred)
print('Confusion Matrix\n',cm)


disp = ConfusionMatrixDisplay(cm, display_labels=['Survived', 'Died'])
disp.plot()
plt.text(1,0.1,'false negatives', color='y', ha='center', fontweight='bold')
plt.text(0,1.1,'false positives', color='y', ha='center', fontweight='bold')

plt.text(0,0.1,'correct postive', color='g', ha='center', fontweight='bold')
plt.text(1,1.1,'correct negative', color='g', ha='center', fontweight='bold')
plt.show()


# In[43]:


print(classification_report(y, y_pred))


# In[44]:


fpr, tpr, thresholds = roc_curve(y, y_pred)
roc_auc = auc(fpr, tpr)
display = RocCurveDisplay(fpr=fpr, tpr=tpr, roc_auc=roc_auc)
display.plot()
plt.text(0.5, 0.5, f'AUC: {round(roc_auc,3)}', fontweight='bold')
plt.legend([])
plt.show()


# In[ ]:




