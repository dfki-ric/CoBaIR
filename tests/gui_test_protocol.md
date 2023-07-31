# Test Protocol


| Starting Condition | Actions | Expected Outcome | Tested for Version|
| --- | --- | --- | --- |
| The application is open and the user is on the main GUI | Click on the "Load" button | A file open dialog box should appear | 4.0.0 |
| The file open dialog box is displayed | Select a .yml file to open and click "Open" | The fields in the application should be filled with the contents from the .yml file | 4.0.0 |
|  The file open dialog box should appear. | Select a file with an invalid format (e.g., .txt) and click "Open." | An error message should be displayed | 4.0.0 |
| The user is on the main GUI | Click on the "New Context" button | A dialog window should appear | 4.0.0 |
| The New Context dialog window is displayed | Enter a new context in the input field and press "OK" | The new context should be added to the list of available contexts in the GUI | 4.0.0 |
| The New Context dialog window is displayed | Enter a new context in the input field and press "Cancel" | Nothing should be added to the GUI | 4.0.0 |
| The user is on the main GUI and there is at least one context in the dropdown list | Click on the "Delete" button next to a context | The dropdown item should be removed from the list, along with its instantiation name and apriori probability | 4.0.0 |
| The user is on the main GUI and there is at least one context in the dropdown list | Click on the "Edit" button next to a context | The New Context dialog window should appear, loaded with the context, instantiation name, and apriori probability | 4.0.0 |
| The New Context dialog window is displayed with the loaded context | Edit the context, instantiation name, apriori probability, and press "OK" | The edited context should be added to the list in the GUI | 4.0.0 |
| The user is on the New Context dialog window. |  Leave the input field for the new context name empty and click "OK." | An error message should be displayed, indicating that the context name cannot be empty. | 4.0.0 |
| The user is on the main GUI and there is at least one context in the dropdown list | Select a context from the dropdown | The instantiation name and apriori probability of the selected context should be loaded | 4.0.0 |
| The user is on the main GUI and there is at least one context in the dropdown list | Select a context from the dropdown | The influence of the selected context should be loaded | 4.0.0 |
| The user is on the main GUI and there is at least one intention in the dropdown list | Select a intention from the dropdown | The influence of the selected intention should be loaded | 4.0.0 |
| The user is on the main GUI | Click on the "New Intention" button | A dialog window should appear | 4.0.0 |
| The New Intention dialog window is displayed | Enter a new Intention in the input field and press "OK" | The new intention should be added to the list of available intentions in the GUI | 4.0.0 |
| The New Intention dialog window is displayed | Enter a new Intention in the input field and press "Cancel" | Nothing should be added to the GUI | 4.0.0 |
| The user is on the main GUI and there is at least one Intention in the dropdown list | Click on the "Delete" button next to an intention | The dropdown item should be removed from the list | 4.0.0 |
| The user is on the main GUI and there is at least one Intention in the dropdown list | Click on the "Edit" button next to a Intention | The New Intention dialog window should appear with the loaded intention | 4.0.0 |
| The New Intention dialog window is displayed with the loaded intention | Edit the intention, and press "OK" | The edited intention should be added to the list in the GUI | 4.0.0 |
| The user is on the main GUI | Click on the "advanced" | The table should be unfolded or folded | 4.0.0 |
| The user is on the main GUI | Click on the "remove" button | The respective row should be deleted | 4.0.0 |
| The user is on the main GUI | Click on the "new combined context influence" button |  A dialog window should appear with fields for intention, context, instantiation, and influence value | 4.0.0 |
| A dialog window is displayed with loaded intention, context, instantiation |  Select an intention, context, instantiation, and influence value from the dropdown and click "OK" | The selected intention, context, instantiation, influence value should be loaded in the table | 4.0.0 |
| A dialog window is displayed with loaded intention, context, instantiation |  Select a intention, context, instantiation, influence value from the dropdown and click "Cancel" | Nothing should be added to the GUI | 4.0.0 |
| The user is on the "New Combined Context Influence" dialog window. | Select an intention, context, instantiation, and enter an invalid influence value (e.g., a non-numeric value) and click "OK." | An error message should be displayed, indicating that the influence value should be a numeric value. | 4.0.0 |
|  The user has a large .yml file (greater than 100MB). |  Click on the "Load" button and select the large .yml file. | The application should handle the large file without freezing or crashing, and the fields should be filled with the contents from the .yml file. | 4.0.0 |
| The user has added multiple combined context influences, filling up the table. | Click on the "New Combined Context Influence" button and add another entry to the table. | The application should handle the addition gracefully, allowing the user to scroll through the table entries if needed. | 4.0.0 |
| The user is on the main GUI | Click on the "Save" button | A file loading dialog box should appear, and the file should be saved in .yml format | 4.0.0 |
| The user is on the main GUI | Press Ctrl+O or click on the "Open" button in the menu bar | A file open dialog box should appear | 4.0.0 |
| The user is on the main GUI | Press Ctrl+N or click on the "New" button in the menu bar | A new, empty GUI should appear | 4.0.0 |
| The application is open and the user has made changes to the current file | Press Ctrl+S or click on the "Save" button in the menu bar | The changes should be saved to the current file | 4.0.0 |
| The application is open and the user wants to save the current file with a new name | Press Ctrl+Shift+S or click on the "Save As" button in the menu bar | A file save dialog box should appear, allowing the user to choose a new name and location for the file | 4.0.0 |
| The application is open and the user is on the main GUI | Press F1 or click on the "Help --> Documentation" button in the menu bar | The documentation page for the application should load in the user's default web browser | 4.0.0 |
| The user is on the main GUI with a graph containing multiple contexts | Click on a node representing a context in the graph | The GUI should update to display detailed information related to the selected context | 4.0.0 |
|The user is on the main GUI with a graph containing intentions |  Click on a node representing an intention in the graph | The GUI should update to display detailed information related to the selected intention | 4.0.0 |
| The application is open and the user is on the main GUI |  Perform various interactions with the application, such as clicking buttons, selecting options, and editing fields | The application should respond promptly to user actions, without noticeable lag or delays | 4.0.0 |
| The user has made changes to the current file |  Close the application without saving changes or click on the "Discard Changes" button | The application should prompt the user to confirm discarding changes, preventing accidental data loss | 4.0.0 |
| The application is open and running | Intentionally trigger specific errors (e.g., network error, file not found, invalid data format) and observe the application's response | The application should display appropriate error messages and handle errors gracefully, without crashing or becoming unresponsive | 4.0.0 |