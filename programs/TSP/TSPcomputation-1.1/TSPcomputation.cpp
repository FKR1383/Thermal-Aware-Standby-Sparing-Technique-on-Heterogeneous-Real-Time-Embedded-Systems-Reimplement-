/**	\file	TSPcomputation.cpp
 *	\brief	Main source file of the application.
 */

#include "TSPcomputation.h"





/**	\brief	Main function of the application.
 *
 */
int main(int argc, char *argv[])
{
	ConfigurationParameters configurationParameters;

	// Read the configuration from the command line
	configurationParameters.parseCommandLine(argc, argv);

	// Verify the configuration
	if(configurationParameters.verify() == false){
		cout << "Error: The configuration has some invalid parameters." << endl;
		exit(-1);
	}


	// Read the B matrix from the input file and obtain the inverse of the B matrix
	double** Binv;
	int numberThermalNodes;
	if(readBinvMatrix(configurationParameters.bMatrixFileName, Binv, numberThermalNodes) == false){
		exit(-1);
	}




	// Read the G vector from the input file
	double *G;
	if(readGvector(configurationParameters.gVectorFileName, G, numberThermalNodes) == false){
		for(int i = 0; i < numberThermalNodes; i++){
			delete[] Binv[i];
		}
		delete[] Binv;
		delete[] G;

		exit(-1);
	}


	// Check that the number of cores and number of blocks from the command line does not exceed the size of the B matrix
	if((configurationParameters.numberOfCores > numberThermalNodes) || (configurationParameters.numberOfBlocks > numberThermalNodes)){
		cout << "Error: The configuration has some invalid parameters. There cannot be more cores or blocks than thermal elements in the B matrix." << endl;

		for(int i = 0; i < numberThermalNodes; i++){
			delete[] Binv[i];
		}
		delete[] Binv;
		delete[] G;

		exit(-1);
	}



	// Read the power in other blocks
	double* Pblocks;
	if(readPblocks(configurationParameters.pBlocksTraceFileName, configurationParameters.numberOfCores, configurationParameters.numberOfBlocks, numberThermalNodes, Pblocks) == false){
		for(int i = 0; i < numberThermalNodes; i++){
			delete[] Binv[i];
		}
		delete[] Binv;
		delete[] G;
		delete[] Pblocks;

		exit(-1);
	}
	double totalPowerPblocks = 0;
	for(unsigned int i = 0; i < numberThermalNodes; i++){
		totalPowerPblocks += Pblocks[i];
	}




	// Print the configuration parameters for which to compute TSP
	cout << "TSP configuration:" << endl;
	cout << "\tNumber of cores: " << configurationParameters.numberOfCores << endl;
	cout << "\tT_amb: " << configurationParameters.Tamb - Tkelvin << " °C" << endl;
	cout << "\tT_dtm: " << configurationParameters.Tdtm - Tkelvin << " °C" << endl;
	cout << "\tP_max: " << configurationParameters.Pmax << " Watts" << endl;
	cout << "\tP_inactive_core: " << configurationParameters.PinactiveCore << " Watts" << endl << endl;





	// If there was no input mapping file, then we compute TSP for the worst-case core mappings.
	if(configurationParameters.givenCoreMappingFileName.size() <= 0){
		vector<double> tspValues;
		vector< vector<int> > listCoresWorstCase;


		// First, build matrix H
		vector< vector<HeatContribution> > matrixH;
		for(int i = 0; i < configurationParameters.numberOfBlocks; i++){
			vector<HeatContribution> rowMatrixH;
			for(int j = 0; j < configurationParameters.numberOfCores; j++){
				HeatContribution auxHelement;
				auxHelement.coreIndex = j;
				auxHelement.heatContribution = Binv[i][j];
				rowMatrixH.push_back(auxHelement);
			}
			sort(rowMatrixH.begin(), rowMatrixH.end());
			reverse(rowMatrixH.begin(),rowMatrixH.end());
			matrixH.push_back(rowMatrixH);
		}


		// Now compute TSP for all values of m
		for(int m = 0; m < configurationParameters.numberOfCores; m++){
			// First compute Pstar
			double PworstStar = DBL_MAX;
			int coreIndexPworstStar = -1;
			for(int i = 0; i < configurationParameters.numberOfBlocks; i++){

				// Compute the sum of matrix H from j = 1 to j = m
				double firstHalfH = 0;
				for(int j = 0; j <= m; j++){
					firstHalfH += matrixH[i][j].heatContribution;
				}
				// Compute the sum of matrix H from j = m + 1 to j = M'
				double lastHalfH = 0;
				for(int j = m + 1; j < configurationParameters.numberOfCores; j++){
					lastHalfH += matrixH[i][j].heatContribution;
				}
				// Compute the heat contributed by the active blocks and ambient temperature
				double heatBlocksAndAmbient = 0;
				for(int j = 0; j < numberThermalNodes; j++){
					heatBlocksAndAmbient += Binv[i][j] * ( Pblocks[j] + configurationParameters.Tamb * G[j] );
				}

				double auxP = configurationParameters.Tdtm - configurationParameters.PinactiveCore * lastHalfH;
				auxP = auxP - heatBlocksAndAmbient;
				auxP = auxP / firstHalfH;

				if(auxP < PworstStar){
					PworstStar = auxP;
					coreIndexPworstStar = i;
				}
			}


			// Now compute TSP according to Pstar and Pmax
			double maxTSP = configurationParameters.PinactiveCore + (configurationParameters.Pmax - totalPowerPblocks - configurationParameters.numberOfCores * configurationParameters.PinactiveCore) / m;
			if(PworstStar <= maxTSP)
				tspValues.push_back(PworstStar);
			else
				tspValues.push_back(maxTSP);


			// Save the list of cores that resulted in the worst-case
			if(coreIndexPworstStar >= 0){
				vector<int> partialListCoresWorstCase;
				for(int j = 0; j < configurationParameters.numberOfCores; j++){
					bool coreInWorstCaseList = false;
					for(int h = 0; h <= m; h++){
						if(matrixH[coreIndexPworstStar][h].coreIndex == j)
							coreInWorstCaseList = true;
					}

					if(coreInWorstCaseList)
						partialListCoresWorstCase.push_back(1);
					else
						partialListCoresWorstCase.push_back(0);
				}
				listCoresWorstCase.push_back(partialListCoresWorstCase);
			}
		}




		// Now print out the worst-case mappings of core
		for(unsigned int i = 0; i < listCoresWorstCase.size(); i++){
			cout << "listCoresWorstCase(" << i+1 << ",:) =  [ ";
			for(int j = 0; j < (int)listCoresWorstCase[i].size() - 1; j++){
				cout << listCoresWorstCase[i][j] << ", ";
			}
			cout << listCoresWorstCase[i][listCoresWorstCase[i].size() - 1] << "];" << endl;
		}
		cout << endl;

		// And print the worst-case TSP uniform power constraints
		for(int i = 0; i < configurationParameters.numberOfCores; i++){
			cout << "TSP per-core(" << i + 1 << ") [Watts]: " << tspValues[i] << endl;
		}




		// Also save the worst-case mappings of cores and TSP values into a file if required
		if(configurationParameters.outputFileName.size() > 0){
			ofstream outputFile;
			outputFile.open(configurationParameters.outputFileName.c_str());
			if(outputFile.good()){
				for(unsigned int i = 0; i < listCoresWorstCase.size(); i++){
					outputFile << "listCoresWorstCase(" << i+1 << ",:) =  [ ";
					for(int j = 0; j < (int)listCoresWorstCase[i].size() - 1; j++){
						outputFile << listCoresWorstCase[i][j] << ", ";
					}
					outputFile << listCoresWorstCase[i][listCoresWorstCase[i].size() - 1] << "];" << endl;
				}
				outputFile << endl;

				for(int i = 0; i < configurationParameters.numberOfCores; i++){
					outputFile << "TSPworst(" << i + 1 << ") = " << tspValues[i] << endl;
				}

				if(outputFile.good() == false){
					cout << "Error: There was an error while writing to the TSP output file." << endl;
				}
				outputFile.close();
			}
			else{
				cout << "Error: The TSP output file could not be open for writing." << endl;
			}
		}
	}
	else{
		double tspValue;

		short int* givenMapping;
		if(readGivenMapping(configurationParameters.givenCoreMappingFileName, configurationParameters.numberOfCores, givenMapping) == false){
			for(int i = 0; i < numberThermalNodes; i++){
				delete[] Binv[i];
			}
			delete[] Binv;
			delete[] G;
			delete[] Pblocks;
			delete[] givenMapping;

			exit(-1);
		}
		int numberActiveCores = 0;
		for(int i = 0; i < configurationParameters.numberOfCores; i++){
			numberActiveCores += givenMapping[i];
		}

		double PworstStar = DBL_MAX;
		int coreIndexPworstStar = -1;
		for(int i = 0; i < configurationParameters.numberOfBlocks; i++){

			double heatContributionInactiveCores = 0;
			double heatContributionActiveCores = 0;

			// Compute the heat contributed by the inactive cores and the active cores
			for(int j = 0; j < configurationParameters.numberOfCores; j++){
				heatContributionInactiveCores += Binv[i][j] * (1 - givenMapping[j]);
				heatContributionActiveCores += Binv[i][j] * givenMapping[j];
			}

			// Compute the heat contributed by the active blocks and ambient temperature
			double heatBlocksAndAmbient = 0;
			for(int j = 0; j < numberThermalNodes; j++){
				heatBlocksAndAmbient += Binv[i][j] * ( Pblocks[j] + configurationParameters.Tamb * G[j] );
			}

			double auxP = configurationParameters.Tdtm - configurationParameters.PinactiveCore*heatContributionInactiveCores;
			auxP = auxP - heatBlocksAndAmbient;
			auxP = auxP / heatContributionActiveCores;

			if(auxP < PworstStar){
				PworstStar = auxP;
				coreIndexPworstStar = i;
			}
		}


		// Now compute TSP according to Pstar and Pmax
		double maxTSP = configurationParameters.PinactiveCore + (configurationParameters.Pmax - totalPowerPblocks - configurationParameters.numberOfCores * configurationParameters.PinactiveCore) / numberActiveCores;
		if(PworstStar <= maxTSP)
			tspValue = PworstStar;
		else
			tspValue = maxTSP;


		cout << "TSP per-core (given mapping with " << numberActiveCores << " active cores) [Watts]: " << tspValue << endl;



		// Also save the TSP value for the given mapping into a file if required
		if(configurationParameters.outputFileName.size() > 0){
			ofstream outputFile;
			outputFile.open(configurationParameters.outputFileName.c_str());
			if(outputFile.good()){
				outputFile << "givenMapping(" << numberActiveCores << ",:) =  [ ";
				for(int j = 0; j < configurationParameters.numberOfCores - 1; j++){
					outputFile << givenMapping[j] << ", ";
				}
				outputFile << givenMapping[configurationParameters.numberOfCores - 1] << "];" << endl << endl;

				outputFile << "TSP(givenMapping) = " << tspValue << endl;

				if(outputFile.good() == false){
					cout << "Error: There was an error while writing to the TSP output file." << endl;
				}
				outputFile.close();
			}
			else{
				cout << "Error: The TSP output file could not be open for writing." << endl;
			}
		}

		delete[] givenMapping;
	}



	for(int i = 0; i < numberThermalNodes; i++){
		delete[] Binv[i];
	}
	delete[] Binv;
	delete[] G;
	delete[] Pblocks;





	exit(0);
}










bool readBinvMatrix(const string &fileName, double** &Binv, int &numberThermalNodes)
{
	Matrix<double, Dynamic, Dynamic> B;

	if(fileName.size() > 0){
		ifstream inputFile(fileName.c_str());
		if ( inputFile.is_open() ){
			if(inputFile.good()){
				// Read until the end of the file
				while(inputFile.good()){
					// Read one line from the file
					string line;
					getline(inputFile, line);

					// If the line was successfully read
					if(inputFile.good()){

						// Look for the start of the matrix
						if(line.find("matrix b:") != string::npos){
							// Read one line from the file until we read an empty line
							string lineBvalues;
							getline(inputFile, lineBvalues);

							int lineNumber = 0;

							while(lineBvalues.size() > 0){

								try{
									double dValue;
									stringstream lineStream(lineBvalues);
									lineStream.exceptions(stringstream::goodbit);

									// If this is the first line read, then read the entire line and resize matrix B to this size
									if(lineNumber == 0){
										vector< double > lineValues;

										// Read the entire line
										while(lineStream.good()){
											lineStream >> dValue;
											if((lineStream.rdstate() == stringstream::goodbit) || (lineStream.rdstate() == stringstream::eofbit)){
												lineValues.push_back(dValue);
											}
										}

										if(lineValues.size() > 0){
											B.resize(lineValues.size(), lineValues.size());
										}
										else{
											cout << "Error: The number of rows and columns in the file with the information of the B matrix is not consistent. " << endl;
											inputFile.close();
											return false;
										}

										for(unsigned int i = 0; i < lineValues.size(); i++){
											B(0,i) = lineValues[i];
										}
									}
									// If it is not the first line, then read the line and check that the matrix size is consistent
									else{
										if(lineNumber < B.rows()){
											int numberColumns = 0;
											// Read the entire line
											while(lineStream.good()){
												lineStream >> dValue;
												if((lineStream.rdstate() == stringstream::goodbit) || (lineStream.rdstate() == stringstream::eofbit)){
													B(lineNumber,numberColumns) = dValue;
													numberColumns++;
												}
											}

											if(numberColumns != B.cols()){
												cout << "Error: The number of rows and columns in the file with the information of the B matrix is not consistent. " << endl;
												inputFile.close();
												return false;
											}
										}
										else{
											cout << "Error: The number of rows and columns in the file with the information of the B matrix is not consistent. " << endl;
											inputFile.close();
											return false;
										}
									}

									lineNumber++;
								}
								catch(...){
									cout << "Error: B matrix file is invalid." << endl;
									inputFile.close();
									return false;
								}

								getline(inputFile, lineBvalues);
							}
						}
					}
				}

				inputFile.close();
			}
			else{
				cout << "Error: File with the information of the B matrix could not be open for reading." << endl;
				inputFile.close();
				return false;
			}
		}
		else{
			cout << "Error: File with the information of the B matrix could not be open for reading." << endl;
			return false;
		}
	}


	Matrix<double, Dynamic, Dynamic> BinvMatrix;
	BinvMatrix = B.inverse();
	numberThermalNodes = B.rows();

	if((numberThermalNodes != BinvMatrix.rows()) || (numberThermalNodes != BinvMatrix.cols())){
		cout << "Error: The input matrix B is not a square matrix." << endl;
		return false;
	}


	Binv = new double*[numberThermalNodes];
	for(int i = 0; i < numberThermalNodes; i++){
		Binv[i] = new double[numberThermalNodes];
		for(int j = 0; j < numberThermalNodes; j++){
			Binv[i][j] = BinvMatrix(i,j);
		}
	}


	return true;
}




bool readGvector(const string &fileName, double* &G, const int &numberThermalNodes)
{
	G = new double[numberThermalNodes];

	if(fileName.size() > 0){
		ifstream inputFile(fileName.c_str());
		if ( inputFile.is_open() ){
			if(inputFile.good()){
				// Read until the end of the file
				while(inputFile.good()){
					// Read one line from the file
					string line;
					getline(inputFile, line);

					// If the line was successfully read
					if(inputFile.good()){

						// Look for the start of the vector
						if((line.find("vector g_amb:") != string::npos) || (line.find("vector g:") != string::npos)){
							// Read one line from the file until we read an empty line
							string lineGvalues;
							getline(inputFile, lineGvalues);

							try{
								double dValue;
								stringstream lineStream(lineGvalues);
								lineStream.exceptions(stringstream::goodbit);

								vector< double > lineValues;

								// Read the entire line
								while(lineStream.good()){
									lineStream >> dValue;
									if((lineStream.rdstate() == stringstream::goodbit) || (lineStream.rdstate() == stringstream::eofbit)){
										lineValues.push_back(dValue);
									}
								}

								if(lineValues.size() <= 0){
									cout << "Error: The number of columns in the file with the information of the G vector is invalid. " << endl;
									inputFile.close();
									return false;
								}

								int offset = numberThermalNodes - lineValues.size();
								if(offset < 0){
									cout << "Error: The number of columns in the file with the information of the G vector is invalid. " << endl;
									inputFile.close();
									return false;
								}

								for(unsigned int i = 0; i < lineValues.size(); i++){
									G[offset + i] = lineValues[i];
								}
							}
							catch(...){
								cout << "Error: G vector file is invalid." << endl;
								inputFile.close();
								return false;
							}
						}
					}
				}

				inputFile.close();
			}
			else{
				cout << "Error: File with the information of the G vector could not be open for reading." << endl;
				inputFile.close();
				return false;
			}
		}
		else{
			cout << "Error: File with the information of the G vector could not be open for reading." << endl;
			return false;
		}
	}

	return true;
}




bool readPblocks(const string &fileName, const int &numberOfCores, const int &numberOfBlocks, const int &numberThermalNodes, double* &Pblocks)
{
	Pblocks = new double[numberThermalNodes];
	for(int i = 0; i < numberThermalNodes; i++){
		Pblocks[i] = 0;
	}

	if(fileName.size() > 0){
		ifstream inputFile(fileName.c_str());
		if ( inputFile.is_open() ){
			if(inputFile.good()){

				vector< double > readValues;

				// Read until the end of the file
				while(inputFile.good()){
					// Read one line from the file
					string line;
					getline(inputFile, line);

					// If the line was successfully read and has data in it
					if(inputFile.good() && (line.size() > 0)){

						// If the line was not a comment
						if(line[0] != '#'){

							try{
								double dValue;
								stringstream lineStream(line);
								lineStream.exceptions(stringstream::goodbit);

								// Read the entire line
								while(lineStream.good()){
									lineStream >> dValue;
									if((lineStream.rdstate() == stringstream::goodbit) || (lineStream.rdstate() == stringstream::eofbit)){
										readValues.push_back(dValue);
									}
								}
							}
							catch(...){
								cout << "Error: File with the power in other blocks is invalid." << endl;
								inputFile.close();
								return false;
							}
						}
					}
				}

				inputFile.close();



				if((numberOfCores + readValues.size()) == numberOfBlocks){
					for(unsigned int i = 0; i < readValues.size(); i++){
						Pblocks[numberOfCores + i] = readValues[i];
					}
				}
				else{
					cout << "Error: Too many lines in the file with the power in other blocks." << endl;
					return false;
				}
			}
			else{
				cout << "Error: File with the power in other blocks could not be open for reading." << endl;
				inputFile.close();
				return false;
			}
		}
		else{
			cout << "Error: File with the power in other blocks could not be open for reading." << endl;
			return false;
		}
	}

	return true;
}







bool readGivenMapping(const string &fileName, const int &numberOfCores, short int* &givenMapping)
{
	givenMapping = new short int[numberOfCores];
	for(int i = 0; i < numberOfCores; i++){
		givenMapping[i] = 0;
	}

	if(fileName.size() > 0){
		ifstream inputFile(fileName.c_str());
		if ( inputFile.is_open() ){
			if(inputFile.good()){

				vector< double > readValues;

				// Read until the end of the file
				while(inputFile.good()){
					// Read one line from the file
					string line;
					getline(inputFile, line);

					// Replace all ',' with withe spaces
					size_t commaPosition;
					while((commaPosition = line.find(',')) != string::npos)
						line.replace(commaPosition, 1, 1, ' ');

					// If the line was successfully read and has data in it
					if(inputFile.good() && (line.size() > 0)){

						// If the line was not a comment
						if(line[0] != '#'){

							try{
								short int iValue;
								stringstream lineStream(line);
								lineStream.exceptions(stringstream::goodbit);

								// Read the entire line
								while(lineStream.good()){
									lineStream >> iValue;
									if((lineStream.rdstate() == stringstream::goodbit) || (lineStream.rdstate() == stringstream::eofbit)){
										if(iValue <= 0)
											readValues.push_back(0);
										else
											readValues.push_back(1);
									}
								}
							}
							catch(...){
								cout << "Error: File with the given mapping of active cores is invalid." << endl;
								inputFile.close();
								return false;
							}
						}
					}
				}

				inputFile.close();



				if(numberOfCores == readValues.size()){
					for(unsigned int i = 0; i < readValues.size(); i++){
						givenMapping[i] = readValues[i];
					}
				}
				else if(numberOfCores < readValues.size()){
					cout << "Error: Too many lines in the file with the given mapping of active cores." << endl;
					return false;
				}
				else{
					cout << "Error: Too few lines in the file with the given mapping of active cores." << endl;
					return false;
				}
			}
			else{
				cout << "Error: File with the given mapping of active cores could not be open for reading." << endl;
				inputFile.close();
				return false;
			}
		}
		else{
			cout << "Error: File with the given mapping of active cores could not be open for reading." << endl;
			return false;
		}
	}

	return true;
}






