# Tuple
- A tuple is an ordered collection of elements enclosed within () - parantheses
- Tuples are immutable - We can't change the elements inside it once we have created it. 
## Extracting individual elements of the tuple
- For the first element we will type 
tuple_name[0]and so on for the next elements 
- For the last element we will type tuple_name[-1]
- To extract a sequence of elements we use the ":" operator 
## Example 
```python
tup1 = (1,2,3,4,5,6)
tup1[1:4]  #this will extract the elements from 2 to 4 
```
- Note : last element is exclusive and first element before the colon in inclusive when we use the ":" Operator to extract the sequemce of elements 

## Tuple Basic operations
- Finding length  of the tuple - Using 'len(Tuple_name)'
- Concatenating tuples - using 'tup1+tup2'
- Reapeating Tuple elements - Tup1*n, This is will give an output tuple with all the elements of the tuple repeated n times.
- Repeating and Concatenating- Tup1*n + Tup2 - This will repeat Tup1 n times and add it with Tup2 simultaenously with a single line of code 

- To find out the minimum value and maximum value present in the Tuple.
- We will need to use the min(), and max() functions.


