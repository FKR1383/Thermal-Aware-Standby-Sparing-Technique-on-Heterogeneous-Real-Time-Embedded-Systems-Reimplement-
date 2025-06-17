/**	\file	configurationParameters.h
 *	\brief	Header file for general configuration parameters.
 */
#ifndef CONFIGURATIONPARAMETERS_H_
#define CONFIGURATIONPARAMETERS_H_

#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <algorithm>
#include <unistd.h>
#include <string.h>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <stdexcept>

using namespace std;



const long double Tkelvin = 273.15;




/**	\brief	Class that stores the configuration parameters.
 *
 *	Class that stores the configuration parameters from the configuration files or the command line. The command line has priority.
 */
class ConfigurationParameters{
public:

	/**	\brief	Structre with the definition pair of strings that forms a configuration parameter.	*/
	struct Parameter {
		string name;										/**< \brief Name of the configuration parameter.	*/
		string value;										/**< \brief Value of the configuration parameter.	*/
	};


	/**	\brief	Vector containing all the configuration parameters.	*/
	vector< Parameter > parameters;



	/**	\brief	Method that parses the command line arguments.
	 *
	 *	\param[in]	argc	Number of command line arguments.
	 *	\param[in]	argv	Strings with the command line arguments.
	 */
	void parseCommandLine(int argc, char *argv[]);



	/**	\brief	Method that verifies that the configuration parameters are valid.
	 *
	 */
	bool verify(void);



	/**	\brief	Method that prints the configuration parameters.
	 */
	void print(void);



	double Tamb;											/**< \brief Ambient temperature [Kelvin].								*/
	double Tdtm;											/**< \brief	Critical temperature in which DTM is triggered [Kelvin].	*/
	double Pmax;											/**< \brief	Maximum chip power [Watts].									*/
	double PinactiveCore;									/**< \brief	Minimum power consumption for an inactive core.				*/
	int numberOfCores;										/**< \brief	Number of cores in the floorplan.							*/
	int numberOfBlocks;										/**< \brief	Number of blocks in the floorplan.							*/
	string pBlocksTraceFileName;							/**< \brief	File name of the trace file with the power consumption of other blocks (other than cores).		*/
	string outputFileName;									/**< \brief	Name of the output file in which to store the TSP values.	*/
	string givenCoreMappingFileName;						/**< \brief	Name of the input file of a core mapping for which to compute TSP.	*/
	string bMatrixFileName;									/**< \brief	Name of the input file with the values of the B matrix.		*/
	string gVectorFileName;									/**< \brief	Name of the input file with the values of the G vector.		*/





	/**	\brief	Constructor. Initializes all variables with the default values.	*/
	ConfigurationParameters();

private:
	/**	\brief	Method that checks whether the name of the new parameter is valid.
	 *
	 *	\param[in]	newParameterName	Name of the new parameter.
	 *	\return							True if the name is valid, false otherwise.
	 */
	bool parameterNameValid(const string &newParameterName);



	/**	\brief	Method that checks whether the value of the new parameter is valid.
	 *
	 *	\param[in]	newParameter		Name and value of the new parameter.
	 *	\param[in]	newHasPriority		When the parameter name is repeated and variable is true, the new value replaces the old one. When this variable is false, the old value is preserved.
	 */
	void addNewParameter(const Parameter &newParameter, const bool &newHasPriority);

};













#endif /* CONFIGURATIONPARAMETERS_H_ */
