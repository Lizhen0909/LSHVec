/**
 * Copyright (c) 2016-present, Facebook, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

#include <iostream>
#include <queue>
#include <iomanip>
#include "fastseq.h"
#include "args.h"

using namespace fasttext;

void printUsage() {
  std::cerr
    << "usage: lshvec <command> <args>\n\n"
    << "The commands supported by lshvec are:\n\n"
    << "  supervised              train a supervised classifier\n"
    << "  quantize                quantize a model to reduce the memory usage\n"
    << "  test                    evaluate a supervised classifier\n"
    << "  predict                 predict most likely labels\n"
    << "  predict-prob            predict most likely labels with probabilities\n"
    << "  skipgram                train a skipgram model\n"
    << "  cbow                    train a cbow model\n"
    << "  print-word-vectors      print word vectors given a trained model\n"
    << "  print-sentence-vectors  print sentence vectors given a trained model\n"
    << "  print-ngrams            print ngrams given a trained model and word\n"
    << "  nn                      query for nearest neighbors\n"
    << "  analogies               query for analogies\n"
    << "  dump                    dump arguments,dictionary,input/output vectors\n"
    << std::endl;
}

void printQuantizeUsage() {
  std::cerr
    << "usage: lshvec quantize <args>"
    << std::endl;
}

void printTestUsage() {
  std::cerr
    << "usage: lshvec test <model> <test-data> [<k>] [<th>]\n\n"
    << "  <model>      model filename\n"
    << "  <test-data>  test data filename (if -, read from stdin)\n"
    << "  <k>          (optional; 1 by default) predict top k labels\n"
    << "  <th>         (optional; 0.0 by default) probability threshold\n"
    << std::endl;
}

void printPredictUsage() {
  std::cerr
    << "usage: lshvec predict[-prob] <model> <test-data> [<k>] [<th>]\n\n"
    << "  <model>      model filename\n"
    << "  <test-data>  test data filename (if -, read from stdin)\n"
    << "  <k>          (optional; 1 by default) predict top k labels\n"
    << "  <th>         (optional; 0.0 by default) probability threshold\n"
    << std::endl;
}

void printPrintWordVectorsUsage() {
  std::cerr
    << "usage: lshvec print-word-vectors <model>\n\n"
    << "  <model>      model filename\n"
    << std::endl;
}

void printPrintSentenceVectorsUsage() {
  std::cerr
    << "usage: lshvec print-sentence-vectors <model>\n\n"
    << "  <model>      model filename\n"
    << std::endl;
}

void printPrintNgramsUsage() {
  std::cerr
    << "usage: lshvec print-ngrams <model> <word>\n\n"
    << "  <model>      model filename\n"
    << "  <word>       word to print\n"
    << std::endl;
}

void quantize(const std::vector<std::string>& args) {
  Args a = Args();
  if (args.size() < 3) {
    printQuantizeUsage();
    a.printHelp();
    exit(EXIT_FAILURE);
  }
  a.parseArgs(args);
  FastSeq fastseq;
  // parseArgs checks if a->output is given.
  fastseq.loadModel(a.output + ".bin");
  fastseq.quantize(a);
  fastseq.saveModel();
  exit(0);
}

void printNNUsage() {
  std::cout
    << "usage: lshvec nn <model> <k>\n\n"
    << "  <model>      model filename\n"
    << "  <k>          (optional; 10 by default) predict top k labels\n"
    << std::endl;
}

void printAnalogiesUsage() {
  std::cout
    << "usage: lshvec analogies <model> <k>\n\n"
    << "  <model>      model filename\n"
    << "  <k>          (optional; 10 by default) predict top k labels\n"
    << std::endl;
}

void printDumpUsage() {
  std::cout
    << "usage: lshvec dump <model> <option>\n\n"
    << "  <model>      model filename\n"
    << "  <option>     option from args,dict,input,output"
    << std::endl;
}

void test(const std::vector<std::string>& args) {
  if (args.size() < 4 || args.size() > 6) {
    printTestUsage();
    exit(EXIT_FAILURE);
  }
  int32_t k = 1;
  real threshold = 0.0;
  if (args.size() > 4) {
    k = std::stoi(args[4]);
    if (args.size() == 6) {
      threshold = std::stof(args[5]);
    }
  }

  FastSeq fastseq;
  fastseq.loadModel(args[2]);

  std::tuple<int64_t, double, double> result;
  std::string infile = args[3];
  if (infile == "-") {
    result = fastseq.test(std::cin, k, threshold);
  } else {
    std::ifstream ifs(infile);
    if (!ifs.is_open()) {
      std::cerr << "Test file cannot be opened!" << std::endl;
      exit(EXIT_FAILURE);
    }
    result = fastseq.test(ifs, k, threshold);
    ifs.close();
  }
  std::cout << "N" << "\t" << std::get<0>(result) << std::endl;
  std::cout << std::setprecision(3);
  std::cout << "P@" << k << "\t" << std::get<1>(result) << std::endl;
  std::cout << "R@" << k << "\t" << std::get<2>(result) << std::endl;
  std::cerr << "Number of examples: " << std::get<0>(result) << std::endl;
}

void predict(const std::vector<std::string>& args) {
  if (args.size() < 4 || args.size() > 6) {
    printPredictUsage();
    exit(EXIT_FAILURE);
  }
  int32_t k = 1;
  real threshold = 0.0;
  if (args.size() > 4) {
    k = std::stoi(args[4]);
    if (args.size() == 6) {
      threshold = std::stof(args[5]);
    }
  }

  bool print_prob = args[1] == "predict-prob";
  FastSeq fastseq;
  fastseq.loadModel(std::string(args[2]));

  std::string infile(args[3]);
  if (infile == "-") {
    fastseq.predict(std::cin, k, print_prob, threshold);
  } else {
    std::ifstream ifs(infile);
    if (!ifs.is_open()) {
      std::cerr << "Input file cannot be opened!" << std::endl;
      exit(EXIT_FAILURE);
    }
    fastseq.predict(ifs, k, print_prob, threshold);
    ifs.close();
  }

  exit(0);
}

void printWordVectors(const std::vector<std::string> args) {
  if (args.size() != 3) {
    printPrintWordVectorsUsage();
    exit(EXIT_FAILURE);
  }
  FastSeq fastseq;
  fastseq.loadModel(std::string(args[2]));
  std::string word;
  Vector vec(fastseq.getDimension());
  while (std::cin >> word) {
    fastseq.getWordVector(vec, word);
    std::cout << word << " " << vec << std::endl;
  }
  exit(0);
}

void printSentenceVectors(const std::vector<std::string> args) {
  if (args.size() != 3) {
    printPrintSentenceVectorsUsage();
    exit(EXIT_FAILURE);
  }
  FastSeq fastseq;
  fastseq.loadModel(std::string(args[2]));
  Vector svec(fastseq.getDimension());
  while (std::cin.peek() != EOF) {
    fastseq.getSentenceVector(std::cin, svec);
    // Don't print sentence
    std::cout << svec << std::endl;
  }
  exit(0);
}

void printNgrams(const std::vector<std::string> args) {
  if (args.size() != 4) {
    printPrintNgramsUsage();
    exit(EXIT_FAILURE);
  }
  FastSeq fastseq;
  fastseq.loadModel(std::string(args[2]));
  fastseq.ngramVectors(std::string(args[3]));
  exit(0);
}

void nn(const std::vector<std::string> args) {
  int32_t k;
  if (args.size() == 3) {
    k = 10;
  } else if (args.size() == 4) {
    k = std::stoi(args[3]);
  } else {
    printNNUsage();
    exit(EXIT_FAILURE);
  }
  FastSeq fastseq;
  fastseq.loadModel(std::string(args[2]));
  std::string queryWord;
  std::shared_ptr<const DictionarySeq> dict = fastseq.getDictionarySeq();
  Vector queryVec(fastseq.getDimension());
  Matrix wordVectors(dict->nwords(), fastseq.getDimension());
  std::cerr << "Pre-computing word vectors...";
  fastseq.precomputeWordVectors(wordVectors);
  std::cerr << " done." << std::endl;
  std::set<std::string> banSet;
  std::cout << "Query word? ";
  std::vector<std::pair<real, std::string>> results;
  while (std::cin >> queryWord) {
    banSet.clear();
    banSet.insert(queryWord);
    fastseq.getWordVector(queryVec, queryWord);
    fastseq.findNN(wordVectors, queryVec, k, banSet, results);
    for (auto& pair : results) {
      std::cout << pair.second << " " << pair.first << std::endl;
    }
    std::cout << "Query word? ";
  }
  exit(0);
}

void analogies(const std::vector<std::string> args) {
  int32_t k;
  if (args.size() == 3) {
    k = 10;
  } else if (args.size() == 4) {
    k = std::stoi(args[3]);
  } else {
    printAnalogiesUsage();
    exit(EXIT_FAILURE);
  }
  FastSeq fastseq;
  fastseq.loadModel(std::string(args[2]));
  fastseq.analogies(k);
  exit(0);
}

void train(const std::vector<std::string> args) {
  Args a = Args();
  a.parseArgs(args);
  FastSeq fastseq;
  std::ofstream ofs(a.output+".bin");
  if (!ofs.is_open()) {
    throw std::invalid_argument(a.output + ".bin cannot be opened for saving.");
  }
  ofs.close();
  fastseq.train(a);
  fastseq.saveModel();
  fastseq.saveVectors();
  if (a.saveOutput) {
    fastseq.saveOutput();
  }
}

void dump(const std::vector<std::string>& args) {
  if (args.size() < 4) {
    printDumpUsage();
    exit(EXIT_FAILURE);
  }

  std::string modelPath = args[2];
  std::string option = args[3];

  FastSeq fastseq;
  fastseq.loadModel(modelPath);
  if (option == "args") {
    fastseq.getArgs().dump(std::cout);
  } else if (option == "dict") {
    fastseq.getDictionarySeq()->dump(std::cout);
  } else if (option == "input") {
    if (fastseq.isQuant()) {
      std::cerr << "Not supported for quantized models." << std::endl;
    } else {
      fastseq.getInputMatrix()->dump(std::cout);
    }
  } else if (option == "output") {
    if (fastseq.isQuant()) {
      std::cerr << "Not supported for quantized models." << std::endl;
    } else {
      fastseq.getOutputMatrix()->dump(std::cout);
    }
  } else {
    printDumpUsage();
    exit(EXIT_FAILURE);
  }
}

int main(int argc, char** argv) {
  std::vector<std::string> args(argv, argv + argc);
  if (args.size() < 2) {
    printUsage();
    exit(EXIT_FAILURE);
  }
  std::string command(args[1]);
  if (command == "skipgram" || command == "cbow" || command == "supervised") {
    train(args);
  } else if (command == "test") {
    test(args);
  } else if (command == "quantize") {
    quantize(args);
  } else if (command == "print-word-vectors") {
    printWordVectors(args);
  } else if (command == "print-sentence-vectors") {
    printSentenceVectors(args);
  } else if (command == "print-ngrams") {
    printNgrams(args);
  } else if (command == "nn") {
    nn(args);
  } else if (command == "analogies") {
    analogies(args);
  } else if (command == "predict" || command == "predict-prob") {
    predict(args);
  } else if (command == "dump") {
    dump(args);
  } else {
    printUsage();
    exit(EXIT_FAILURE);
  }
  return 0;
}
