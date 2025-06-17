/**	\file	configurationParameters.cpp
 *	\brief	Source file for general configuration parameters.
 */

#include "configurationParameters.h"




ConfigurationParameters::ConfigurationParameters()
{
	// Set defaults values for all configuration parameters
	numberOfCores = 0;
	numberOfBlocks = 0;
	Tamb = Tkelvin + 45;
	Tdtm = Tkelvin + 80;
	Pmax = 250;
	PinactiveCore = 0;
	pBlocksTraceFileName = "";
	outputFileName = "";
	givenCoreMappingFileName = "";
	bMatrixFileName = "";
	gVectorFileName = "";
}




void ConfigurationParameters::parseCommandLine(int argc, char *argv[])
{
	// Iterate through the command line
	int i = 1;
	while(i < argc){
		// Depending on the position of the string, it should be a parameter name or a value. Since we start with i=1, it has to be a name.
		// A parameter name, it should start with '-'
		if(argv[i][0] == '-'){
			Parameter newParameter;
			newParameter.name = &(argv[i][1]);
			i++;

			// Check if it is a valid name
			if(parameterNameValid(newParameter.name)){

				// Check if the new parameter has a value, or if there is no value after the parameter name
				if(i < argc){
					newParameter.value = argv[i];
					i++;

					// If valid, add the configuration parameter to the list
					addNewParameter(newParameter, true);
				}
				else{
					cout << "Error: Invalid command line. Parameter \"" << newParameter.name << "\" has no value. Please check usage." << endl;
					exit(1);
				}
			}
			else{
				cout << "Error: Invalid command line. Parameter name \"" << newParameter.name << "\" is invalid. Please check usage." << endl;
				exit(1);
			}
		}
		else{
			cout << "Error: Invalid command line. Please check usage." << endl;
			exit(1);
		}
	}
}






bool ConfigurationParameters::verify(void)
{
	if(numberOfCores <= 0){
		cout << "Error: The number of cores must be a positive integer value." << endl;
		return false;
	}

	if(Tamb < 0){
		cout << "Error: The ambient temperature cannot be a negative value." << endl;
		return false;
	}

	if(Tdtm < 0){
		cout << "Error: The temperature for triggering DTM cannot be a negative value." << endl;
		return false;
	}

	if(Pmax < 0){
		cout << "Error: The maximum chip power cannot be a negative value." << endl;
		return false;
	}

	if(PinactiveCore < 0){
		cout << "Error: The power of an inactive core cannot be a negative value." << endl;
		return false;
	}

	if(bMatrixFileName.size() <= 0){
		cout << "Error: There is no file with the values for the B matrix." << endl;
		return false;
	}

	if(gVectorFileName.size() <= 0){
		cout << "Error: There is no file with the values for the G vector." << endl;
		return false;
	}


	bool numberOfBlocksGiven = false;
	for(unsigned int i = 0; i < parameters.size(); i++){
		if(parameters[i].name == "n_blocks"){
			numberOfBlocksGiven = true;
			break;
		}
	}

	if(numberOfBlocksGiven){
		if(numberOfBlocks < numberOfCores){
			cout << "Error: The number of blocks must be equal to or greater than the number of cores." << endl;
			return false;
		}
	}
	else{
		numberOfBlocks = numberOfCores;
	}



	return true;
}






void ConfigurationParameters::print(void)
{
	cout << "#Configuration Parameters:" << endl;
	if(parameters.size() == 0){
		cout << "\tNo configuration parameters" << endl;
		return;
	}
	for(unsigned int i = 0; i < parameters.size(); i++){
		cout << "\t" << parameters[i].name << ":\t" << parameters[i].value << endl;
	}
}




bool ConfigurationParameters::parameterNameValid(const string &newParameterName)
{
	if(	(newParameterName == "t_amb") ||
		(newParameterName == "t_dtm") ||
		(newParameterName == "cores") ||
		(newParameterName == "n_blocks") ||
		(newParameterName == "p_max") ||
		(newParameterName == "p_inactive_core") ||
		(newParameterName == "p_blocks") ||
		(newParameterName == "mapping") ||
		(newParameterName == "b") ||
		(newParameterName == "g") ||
		(newParameterName == "o")){

		return true;
	}
	else{
		return false;
	}
}



void ConfigurationParameters::addNewParameter(const Parameter &newParameter, const bool &newHasPriority)
{
	if(newParameter.value.size() > 0){
		// Check if the parameter is repeated.
		int repeatedIndex = -1;
		for(unsigned int existingParameter = 0; existingParameter < parameters.size(); existingParameter++){
			if(newParameter.name == parameters[existingParameter].name)
				repeatedIndex = existingParameter;
		}

		// If it is not repeated or the new one has priority, then we add the value to the configuration if it matches the type.
		if((repeatedIndex < 0) || newHasPriority){


			// Start with the configuration parameters that are names of files
			if(newParameter.name == "p_blocks"){
				pBlocksTraceFileName = newParameter.value;
			}
			else if(newParameter.name == "o"){
				outputFileName = newParameter.value;
			}
			else if(newParameter.name == "mapping"){
				givenCoreMappingFileName = newParameter.value;
			}
			else if(newParameter.name == "b"){
				bMatrixFileName = newParameter.value;
			}
			else if(newParameter.name == "g"){
				gVectorFileName = newParameter.value;
			}
			// Now check the variables of type int
			else if(newParameter.name == "cores"){
				try{
					int iValue;
					stringstream streamValue(newParameter.value);
					streamValue.exceptions(stringstream::goodbit);
					streamValue >> iValue;
					if((streamValue.rdstate() == stringstream::goodbit) || (streamValue.rdstate() == stringstream::eofbit))
						numberOfCores = iValue;
					else
						cout << "Error in configuration file: Value of parameter \"" << newParameter.name << "\" is invalid." << endl;
				}
				catch(...){
					cout << "Error in configuration file: Value of parameter \"" << newParameter.name << "\" is invalid." << endl;
				}
			}
			else if(newParameter.name == "n_blocks"){
				try{
					int iValue;
					stringstream streamValue(newParameter.value);
					streamValue.exceptions(stringstream::goodbit);
					streamValue >> iValue;
					if((streamValue.rdstate() == stringstream::goodbit) || (streamValue.rdstate() == stringstream::eofbit))
						numberOfBlocks = iValue;
					else
						cout << "Error in configuration file: Value of parameter \"" << newParameter.name << "\" is invalid." << endl;
				}
				catch(...){
					cout << "Error in configuration file: Value of parameter \"" << newParameter.name << "\" is invalid." << endl;
				}
			}
			// Finally, we check all the variables of type double
			else{
				try{
					double dValue;
					stringstream streamValue(newParameter.value);
					streamValue.exceptions(stringstream::goodbit);
					streamValue >> dValue;
					if((streamValue.rdstate() == stringstream::goodbit) || (streamValue.rdstate() == stringstream::eofbit)){
						if(newParameter.name == "t_amb"){
							Tamb = dValue + Tkelvin;
						}
						else if(newParameter.name == "t_dtm"){
							Tdtm = dValue + Tkelvin;
						}
						else if(newParameter.name == "p_max"){
							Pmax = dValue;
						}
						else if(newParameter.name == "p_inactive_core"){
							PinactiveCore = dValue;
						}
						else{
							return;
						}
					}
					else
						cout << "Error in configuration file: Value of parameter \"" << newParameter.name << "\" is invalid." << endl;
				}
				catch(...){
					cout << "Error in configuration file: Value of parameter \"" << newParameter.name << "\" is invalid." << endl;
				}
			}



			// If it is not repeated, then we add it to the list
			if(repeatedIndex < 0){
				parameters.push_back(newParameter);
			}
			// If it is repeated and the first value has priority, then we replace it
			else{
				parameters[repeatedIndex] = newParameter;
			}
		}
	}
}
