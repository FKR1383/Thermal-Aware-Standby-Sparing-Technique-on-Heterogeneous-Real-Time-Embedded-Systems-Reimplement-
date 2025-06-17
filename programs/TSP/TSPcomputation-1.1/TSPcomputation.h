/**	\file	TSPcomputation.h
 *	\brief	Main header file of the application.
 */

#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <fstream>
#include <sstream>
#include <vector>
#include <algorithm>
#include <complex>
#include <string>
#include <math.h>
#include <cfloat>
#include <Eigen/Dense>
#include <Eigen/Eigenvalues>

#include "configurationParameters.h"

using namespace std;
using namespace Eigen;




/**	\brief	Function that reads the \f$\mathbf{B}\f$ matrix from the corresponding input file and computes the inverse.
 *
 *	Function that reads the \f$\mathbf{B}\f$ matrix from the corresponding input file and computes the inverse.
 *
 *	\param[in]	fileName			Name of the file with the \f$\mathbf{B}\f$ matrix information.
 *	\param[out]	Binv				Inverse of the \f$\mathbf{B}\f$ matrix.
 *	\param[out]	numberThermalNodes	Number of thermal nodes in the \f$\mathbf{B}\f$ matrix.
 *	\return							True if the file was successfully read and the inverse of the \f$\mathbf{B}\f$ matrix successfully computed. False otherwise.
 */
bool readBinvMatrix(const string &fileName, double** &Binv, int &numberThermalNodes);



/**	\brief	Function that reads the G vector from the corresponding input file.
 *
 *	Function that reads the G vector from the corresponding input file. Note that if the information in the file has less values that rows in the B matrix,
 *	then the first values of the G vector are filled with 0. This is particularly useful when using HotSpot to generate the RC thermal network, as HotSpot outputs a g_amb
 *	vector which includes only the thermal nodes that are in contact with the ambient.
 *
 *	\param[in]	fileName				Name of the file with the \f$\mathbf{G}\f$ vector information.
 *	\param[in]	G						Vector \f$\mathbf{G}\f$.
 *	\param[in]	numberThermalNodes		Number of rows in matrix \f$\mathbf{B}\f$, to know how many leading zeros to add at the beginning of vector \f$\mathbf{G}\f$.
 *	\return								True if the \f$\mathbf{G}\f$ vector was succesfully read. False otherwise.
 */
bool readGvector(const string &fileName, double* &G, const int &numberThermalNodes);



/**	\brief	Function that reads the G vector from the corresponding input file.
 *
 *	Function that reads the G vector from the corresponding input file. Note that if the information in the file has less values that rows in the B matrix,
 *	then the first values of the G vector are filled with 0. This is particularly useful when using HotSpot to generate the RC thermal network, as HotSpot outputs a g_amb
 *	vector which includes only the thermal nodes that are in contact with the ambient.
 *
 *	\param[in]	fileName				Name of the file with the G vector information.
 *	\param[in]	numberOfCores			Number of cores in the floorplan.
 *	\param[in]	numberOfBlocks			Number of blocks in the floorplan.
 *	\param[in]	numberThermalNodes		Number of rows in matrix \f$\mathbf{B}\f$.
 *	\param[out]	Pblocks					Vector \f$\mathbf{P}_\mathrm{blocks}\f$.
 *	\return								True if the vector was successfully read. False otherwise.
 */
bool readPblocks(const string &fileName, const int &numberOfCores, const int &numberOfBlocks, const int &numberThermalNodes, double* &Pblocks);



/**	\brief	Function that reads a given mapping of active cores as input.
 *
 *	Function that reads a given mapping of active cores as input. TSP is later computed for this mapping of active cores.
 *
 *	\param[in]	fileName				Name of the file with the G vector information.
 *	\param[in]	numberOfCores			Number of cores in the floorplan.
 *	\param[out]	givenMapping			Vector with the mapping of active cores.
 *	\return								True if the vector was successfully read. False otherwise.
 */
bool readGivenMapping(const string &fileName, const int &numberOfCores, short int* &givenMapping);





/**	\brief	Class to keep track of the worst-case mapping so it can also be printed as output.	*/
class HeatContribution{
public:
	int coreIndex;							/**< \brief	Index of the core.				*/
	double heatContribution;				/**< \brief	Heat contribution of the core.	*/


	/** \brief	Constructor.	*/
	HeatContribution(){
		coreIndex = 0;
		heatContribution = 0;
	}
};


/**	\brief	Overloaded operator to sort the cores according to their heat contribution.		*/
inline bool operator==(const HeatContribution& lhs, const HeatContribution& rhs){return (lhs.heatContribution == rhs.heatContribution);}

/**	\brief	Overloaded operator to sort the cores according to their heat contribution.		*/
inline bool operator!=(const HeatContribution& lhs, const HeatContribution& rhs){return !operator==(lhs,rhs);}

/**	\brief	Overloaded operator to sort the cores according to their heat contribution.		*/
inline bool operator< (const HeatContribution& lhs, const HeatContribution& rhs){return (lhs.heatContribution < rhs.heatContribution);}

/**	\brief	Overloaded operator to sort the cores according to their heat contribution.		*/
inline bool operator> (const HeatContribution& lhs, const HeatContribution& rhs){return  operator< (rhs,lhs);}

/**	\brief	Overloaded operator to sort the cores according to their heat contribution.		*/
inline bool operator<=(const HeatContribution& lhs, const HeatContribution& rhs){return !operator> (lhs,rhs);}

/**	\brief	Overloaded operator to sort the cores according to their heat contribution.		*/
inline bool operator>=(const HeatContribution& lhs, const HeatContribution& rhs){return !operator< (lhs,rhs);}



