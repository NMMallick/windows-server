## creating your own message file
Create a message file used to generate the proper class for the server to parse. Please refer to the msg file found in the [messages](https://github.com/NMMallick/windows-server/tree/main/scripts/examples/msgs) folder.

Messages can include these primitive datatypes (using c++ declaration syntax):
- Integers (int)
- Floats (float)
- Doubles (double)
- Characters (char)
- Booleans (bool)

As well as non-primitive:
- String (string)

Each datatype can be promoted to an array by appending square brackets to the end of the datatype declaration like so ```int[] my_int```.
Only the newline escape character is allowed after each variable declaration (no whitespaces) and one whitespace is required between the dataype and the variable name.

## generating your message
Once you've create one or more message files, navigate the repositories ```/scripts``` folder so that you can view the generate_msgs.py script.
The script requires three command line inputs:
1. input_path - Path to message files to be used to generate classes
2. output_path - Path to where you'll be creating your publisher and/or subscriber nodes
3. msg_name - Custom name for the message class to be used

```
python generate_msgs.py <path/to/msg/files> <path/to/output/dir> <message_class_name>
```

NOTE: The ```generate_msgs.py``` script will generate all files that match the pattern ```*.msg```

## Making a Publisher/Subscriber
The ```my_publisher.py``` and ```my_subscriber.py``` files go through creating a publisher/subscriber.