# Test Protocol

| Starting Condition | Actions | Expected Outcome |
| --- | --- | --- | 
| The application is open and the user is on the main GUI | Click on the "Load" button | A file upload dialog box should appear |
| The file upload dialog box is displayed | Select a .yml file to upload and click "Open" | The fields in the application should be filled with the contents from the .yml file |
| The user is on the main GUI | Click on the "New Context" button | A dialog window should appear |
| The New Context dialog window is displayed | Enter a new context in the input field and press "OK" | The new context should be added to the list of available contexts in the GUI |
| The New Context dialog window is displayed | Enter a new context in the input field and press "Cancel" | Nothing should be added to the GUI |
| The user is on the main GUI and there is at least one context in the dropdown list | Click on the "Delete" button next to a context | The dropdown item should be removed from the list, along with its instantiation name and apriori probability |
| The user is on the main GUI and there is at least one context in the dropdown list | Click on the "Edit" button next to a context | The New Context dialog window should appear, loaded with the context, instantiation name, and apriori probability |
| The New Context dialog window is displayed with the loaded context | Edit the context, instantiation name, apriori probability, and press "OK" | The edited context should be added to the list in the GUI |
| The user is on the main GUI and there is at least one context in the dropdown list | Select a context from the dropdown | The instantiation name and apriori probability of the selected context should be loaded |
| The user is on the main GUI and there is at least one context in the dropdown list | Select a context from the dropdown | The influence of the selected context should be loaded |
| The user is on the main GUI and there is at least one intention in the dropdown list | Select a intention from the dropdown | The influence of the selected intention should be loaded |
| The user is on the main GUI | Click on the "New Intention" button | A dialog window should appear |
| The New Intention dialog window is displayed | Enter a new Intention in the input field and press "OK" | The new intention should be added to the list of available intentions in the GUI |
| The New Intention dialog window is displayed | Enter a new Intention in the input field and press "Cancel" | Nothing should be added to the GUI |
| The user is on the main GUI and there is at least one Intention in the dropdown list | Click on the "Delete" button next to an intention | The dropdown item should be removed from the list |
| The user is on the main GUI and there is at least one Intention in the dropdown list | Click on the "Edit" button next to a Intention | The New Intention dialog window should appear with the loaded intention |
| The New Intention dialog window is displayed with the loaded intention | Edit the intention, and press "OK" | The edited intention should be added to the list in the GUI |
| The user is on the main GUI | Click on the "advanced" | The table should be unfolded or folded |
| The user is on the main GUI | Click on the "remove" button | The respective row should be deleted |
| The user is on the main GUI | Click on the "new combined context influence" button |  A dialog window should appear with fields for intention, context, instantiation, and influence value |
| A dialog window is displayed with loaded intention, context, instantiation |  Select an intention, context, instantiation, and influence value from the dropdown and click "OK" | The selected intention, context, instantiation, influence value should be loaded in the table |
| A dialog window is displayed with loaded intention, context, instantiation |  Select a intention, context, instantiation, influence value from the dropdown and click "Cancel" | Nothing should be added to the GUI |
| The user is on the main GUI | Click on the "Save" button | A file loading dialog box should appear, and the file should be saved in .yml format | 

