"""
CSAPX Lab03: Least Common Subsumers

Lab03 is to help us become familiar with interacting with the Ontology and
Concept classes from the code provided to us in ontology.py. This will implement two ways of calculating
LCS and a measure of semantic similarity. When ran, the program will load an ontology,
calculate the semantic similarity of every pair of concepts, and then output the list of pairs
in acceding order of similarity.

author: Miguel Reyes
date: 09/13/21
"""
from ontology import Ontology, Concept
from dataclasses import dataclass
import sys

"""
AssociatePair:
    c1(Concept): A concept object (1/2) for the pair
    c2(Concept): A concept object (2/2) for the pair
    similarity(float): the similarity score between c1 and c2
"""


@dataclass
class AssociatePair:
    c1: Concept
    c2: Concept
    similarity: float


def linearLCS(c1: Concept, c2: Concept) -> Concept:
    """
    A linear search to find the Least Common Subsumer between two concepts.
    :param c1: Concept object ex) animal
    :param c2:Concept object ex) lizard
    :return: Concept Object - Least Common Subsumer
    """
    # c1PathList and c2PathList will return the ordered path of concepts from a
    # concept to the top of the hierarchy in the form of a list.
    c1PathList = c1.getPathToTop()
    c2PathList = c2.getPathToTop()
    # Reverse both paths in order n iterate through the paths backwards
    c1PathList.reverse()
    c2PathList.reverse()
    # Check to see which path is smallest because we only need to iterate the length of smallest path amount of times
    # to get the LCS
    if len(c1PathList) < len(c2PathList):
        shorterList = len(c1PathList)
    else:
        shorterList = len(c2PathList)
    # Linear search with two conditions:
    # 1) Once a concept from c1PathList is not equal to c2PathList then look back and return that concept because
    # it was the last equal match
    # 2) If its reached the last concept in the shortest path and that concept is equal to the concept in the other path
    # return that concept
    for i in range(shorterList):
        if c1PathList[i] != c2PathList[i]:
            return c1PathList[i - 1]
        elif i == (shorterList - 1) and c1PathList[i] == c2PathList[i]:
            return c1PathList[i]


def binaryLCS(o: Ontology, c1: Concept, c2: Concept, start, end) -> Concept:
    """
    A recursive Binary Search to find the least common subsumer between two concepts.
    :param o: the ontology object which gives us access to the subsumes method
    :param c1:a concept object
    :param c2:a concept object
    :param start:
    :param end:
    :return:a concept object
    """
    c1PathList = c1.getPathToTop()  # list of c1's path
    mid_index = (start + end) // 2  # the index in the middle of c1PathList
    mid_value = c1PathList[mid_index]  # The value of c1PathList at mid_index
    if start == end:
        # when the start is equal to the end then there is only 1 element left in the updated list and its the item
        # we are searching for
        return mid_value
    elif o.subsumes(mid_value, c2):
        # If mid_value subsumes c2 then we only need to look from the beginning of c1PathList up to the mid_index of
        # the updated list so it keeps calling itself dividing by two until its start == end or it no longer subsumes
        return binaryLCS(o, c1, c2, start, mid_index)
    else:
        # If it does not subsume we look from mid_index + 1 to the end of the updated list and repeat until start
        # == end or it does subsume
        return binaryLCS(o, c1, c2, mid_index + 1, end)


def sim(o: Ontology, c1: Concept, c2: Concept, start, end) -> float:
    """
    The similarity measure defined as the size of the intersection of subsumers
    divided by the size of the union of subsumers.
    :param o: the ontology object needed to perform the binary search
    :param c1: Concept object
    :param c2: Concept object
    :param start: start for binary search
    :param end: end for binary search
    :return: floating point number - the similarity score between c1 and c2
    """
    lcs = binaryLCS(o, c1, c2, start, end)
    s1 = len(c1.getPathToTop())
    s2 = len(c2.getPathToTop())
    s3 = len(lcs.getPathToTop())
    return s3 / (s1 + s2 - s3)


def _partition(lst: list[AssociatePair], pivot: float) \
        -> tuple[list[AssociatePair], list[AssociatePair], list[AssociatePair]]:
    """
    Divides the data into 3 different list(smaller list, equal list, and greater list) depending on the relation
    between the element from the original list and the pivot selected (<, ==, >)

    ***
        I modified the quick_sort method given to us in the rit_sort.py file from professor Strout
        Title: CSAPX Week 3: Searching and Sorting, Author: Sean Strout @ RIT CS, Source: wk03src/rit_sort.py
    ***
    :param lst: The list to be sorted, a list of AssociatePair objects
    :param pivot: The value to partition the data on
    :return: Three list: smaller, equal and greater
    """
    less, equal, greater = [], [], []
    for i in range(len(lst)):
        # iterating through the list given and checking to see if the similarity of the AssociatePair object at lst[
        # i] is less than(appends AssociatePair to less list), greater than(appends AssociatePair to greater list) or
        # equal to(appends AssociatePair to equal list) the pivot
        if lst[i].similarity < pivot:
            less.append(lst[i])
        elif lst[i].similarity > pivot:
            greater.append(lst[i])
        else:
            equal.append(lst[i])
    return less, equal, greater


def quick_sort(lst: list[AssociatePair]) -> list[AssociatePair]:
    """
    Performs a quick sort(recursive function (Out-of-place)) and returns a newly sorted list
    :param lst: The data to be sorted (a list)
    :return: A sorted list
    """
    if len(lst) == 0:
        return []
    else:
        pivot = lst[0].similarity
        less, equal, greater = _partition(lst, pivot)
        # 1) Recursively calls itself until the quick_sort(less) returns an empty list - at this point its down to
        # the smallest element. 2) Then it returns the equal which is the pivot at this stack frame. And then it goes
        # back up the call stack (LIFO) calling quick_sort(greater) repeating steps 1-2
        return quick_sort(less) + equal + quick_sort(greater)


def main():
    """
    Main function - reads a file name from the command line and uses it to create an ontology object. Pairs of concepts
    are created and their similarity scores are calculated. Then the pairs are sorted based off of their similarity
    scores in ascending order. The pairs and their scores are sent to std-output.
    :return:None
    """
    if len(sys.argv) < 2 or len(sys.argv) >= 3:
        # if the argument is less than 2 than their is no file name provided to the command line if its greater
        # than 2 then there are too many arguments provided so the program terminates with the message below to
        # standard input.
        print("Usage: python3 lcs.py filename")
    else:
        o = Ontology("data/" + sys.argv[1] + ".kb")  # instance of Ontology object - gives us access to methods that
        # allow for receiving data like a concept and or a concepts path in the form of a list
        conceptList1 = o.getAllConcepts()  # as the name of the function suggest gets all concepts in the ontology.
        associate_pairs = list()  # empty list where we will store associated pair objects

        # For-loop with a nested for-loop to create a list of associated pair objects
        # The outside for-loop is responsible for c1 or the first value in the associate pair object
        # The nested loop is responsible for the c2 or the 2nd value in the associate pair object
        k = 0  # k allows us to move ahead to a new start in the conceptList2 list after every outside loop iteration
        # so at i = 1 and k = 0, without the k increment, the associated pair would be (m,a) but since we increment k
        # its (m,m)
        for i in range(len(conceptList1)):
            # iterates through conceptList1 [a,m,r,d,c] this will be the values of c1
            c1 = o.getConcept(str(conceptList1[i]))
            for j in range(k, len(conceptList1)):
                # iterates through conceptList1 but after every outside loop iteration this loop will start at k + 1 -
                # at i = 0 k = 0, i = 1 k = 1, this will avoid us having duplicate pairs. This will be the values of c2.
                # We also call the sim function
                c2 = o.getConcept(str(conceptList1[j]))
                similarity = round(sim(o, c1, c2, 0, len(c1.getPathToTop()) - 1), 3)  # returns similarity score
                # between c1 and c2 and is stored to use when creating AssociatePair objects
                associate_pairs.append(AssociatePair(c1, c2, similarity))  # AssociatePair objects appended to
                # associate_pairs empty list - stored in a list so we can sort the objects by their similarity scores
            k += 1
        sorted_pair_list = quick_sort(associate_pairs)  # Sorts AssociatePairs based off of their similarity score in
        # ascending order.
        for i in range(len(sorted_pair_list)):
            # Loop prints out the elements in the sorted_pair_list
            print("sim ( " + str(sorted_pair_list[i].c1) + ", " + str(sorted_pair_list[i].c2) + " ) = " +
                  str(sorted_pair_list[i].similarity))


# The main guard
if __name__ == "__main__":
    main()
