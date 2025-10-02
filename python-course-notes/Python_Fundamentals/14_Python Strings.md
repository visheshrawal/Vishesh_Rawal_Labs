# Python Strings 
- Strings are a sequence of characters enclosed within single quotes(' '), double quotes(" "),or triple quotes(''' ''').
## Examples
'Hello World!' ,"The previous one is a classic",'''I got you laughing didn't I? "

```python
s1 = 'Hello world'
```
## Extracting individual elements of the string
- For the first element we will type 
str_name[0]and so on for the next elements 
- For the last element we will type str_name[-1]
- To extract a sequence of elements we use the ":" operator.
- Note : last element is exclusive and first element before the colon in inclusive when we use the ":" Operator to extract the sequemce of elements 
# String Functions
- Finding length of the string - using len()
- Converting to lower case - my_string.lower()
- Converting to upper case - my_string.upper() 
- Replacing a substring - my_string.replace('blah','mehhhhh')
- Number of occurences of a substring - 
```python
str1 = "hello hello world this is beginners potionn!"
str1.count("hello")
#this will output 2
```
- Finding the index of a substring -
s1= 'I am the devil of my word!"
s1.find('devil")
output= 10

- Splitting a String 
xyz = 'I like mercedes , I like Rolls Royce , I like bugatti'
xyz.split(',')
output = {'I like mercedes','I like Rolls Royce','I like bugatti'}

