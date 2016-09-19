# Setup
## 1. Clone the project
```
git clone git@github.com:N-Thomas/CSynapse.git
```
## 2.Install virtualenv and create virtualenv
```
pip install virtualenv
```
then cd into root dir of project and run:
```
virtualenv venv
```
## 3. Start Virtual Environment
To start the virtual python env in your terminal run
```
source venv/bin/activate
```

## 4.Install dependencies in root of directory
```
pip install -r requirements.txt
```

# Running Project
To run the server:
```
python infrastructure.py
```

# Running All Tests
```
./runTests.sh
```

## Run Individual Test
```
cd Tests
python -m unittest fileName.ClassName.methodName
```
# API

### Get all available algorithms
```
@get /algorithms
@returns list of algorithm ids and descriptions
[{"algoId":"svm", "description":"SVM algorithm"}...]
```

### Get all csynapses for a user
```
@get /csynapses
@returns list of csynapses for a user
[{"csynapses":["test", "hospital data"...]
```

### Create a new csynapse
```
@post /create
@params name=nameOfNewCsynapse
@returns 200 on success
```

### Get all cross validation test results for a csynapse
```
@get /testResults
@returns list of test results for a csynapse 
[{"id":"24324", "score":0.942,"algoId":perceptron", "description":"perceptron algorithm", "time":".21"}...]
```

### Add data to a csynapse
```
@post /data
@params name=nameOfNewCsynapse, upload=fileOfUploadedData
@returns 200 on success
```

### Add data to a csynapse
```
@post /data
@params name=nameOfNewCsynapse, upload=fileOfUploadedData
@returns 200 on success
```

### Test algorithms on a CSynapse
```
@post /test
@params name=csynapseName,algorithm=algoId ... algorithm=algoId
@ returns 200 on success
```

### Test algorithms on a CSynapse
```
@post /test
@params name=csynapseName,algorithm=algoId ... algorithm=algoId
@ returns 200 on success
```

### Get test results for a CSynapse
```
@get /testResults
@params name=csynapseName
@ returns List of test results
[{"id": "57e04a7f3aeb945ad0e28b52", "score": 0.33333333333333326, "algoId": "adaline", "description": "adaline neural network", "time": 0.001},...]
```

### Classifiy new data
```
@post /run
@params name=csynapseName,algorithm=mongoAlgoId, upload=dataToBeClassified
@ returns 200 on success
```

### See available classified data for a user
```
@get /getAllAvailableClassified
@ returns List of available classified data by csynapse -
[{"csynapseName": [{"mongoId": "57e049fa3aeb945ad0e28b48", "datasetName": "irisTest"},...]},{"anotherCsynapse":[{"mongoId":"someId", "datasetName":"mydataSet name"},...]}...]
```

### Get classified data
```
@get /getClassified
@params mongoId=mongoIdOfClassifiedData
@returns data set in body csv
flowerType, headerOne, headerTwo
iris-purple,2,4
iris-black,2,4
...
```

### Get points
```
@get /getPoints
@params name=csynapseName
@returns 2 possibilites: if first time calling this route for a csynapse 200 Ok otherwise 1 up to 3 dimensional points (depending on dimensionality of dataset)
[{"1":{"labelOne":[1,4,6], "labelTwo":[8,9]}, {"2":{"labelOne":[[1,2],[4,5],[8,3]],"labelTwo":[[7,6],[6,4]]}},...}]
```
