from collections import Counter, defaultdict
from pathlib import Path
import re
import regex
import numpy as np
import matplotlib.pyplot as plt
import svgwrite


def greek_char_count(string:str) -> int:
    """Counts the number of Greek characters in a given string."""
    chars = regex.findall( '\p{IsGreek}', string  )
    return len(chars)


def try_open_file( filenames ):
    broken = []
    for filename in filenames:
        try:
            f = open(filename, 'r')
            return f, Path(filename).name
        except:
            broken.append(filename)
    return None, ''


def count_greek_chars(
    filename_prefix:str,
    homily_count:int,
    warning_stdev:float = 1.8,
    output_path:Path|None = None,
    show:bool = False,
):
    page_char_counts = Counter()
    page_to_file_dict = defaultdict(list)

    current_page = "Unk"
    current_folio = None
    current_side = None
    for homily_index in range(homily_count + 1):
        filename = f"{filename_prefix}{homily_index}"
        filename_leadingzero = f"{filename_prefix}0{homily_index}"

        f, current_filename = try_open_file( [ filename, filename_leadingzero, filename + ".txt", filename_leadingzero + ".txt"])
        if not f:
            print("Cannot open", filename)
            continue

        for line in f:
            line = line.strip()
            
            # Check for change of page, e.g.:
            #        |F 71bv|
            match = regex.match(r"\|F (\d+)([vrabcp]+)\|", line)
            if match:
                folio = match.group(1)
                side = match.group(2)
                page = folio + side
                
                if current_folio:
                    if folio != current_folio and int(folio) != int(current_folio) + 1:
                        print(f"Folio error from {current_page} to {page} in file {current_filename} ?")
                    if folio != current_folio and side == current_side and side != 'p':
                        print(f"Folio side error from {current_page} to {page} in file {current_filename} ?")
                    elif folio != current_folio and side != 'r' and side != 'p':
                        print(f"Folio side error from {current_page} to {page} in file {current_filename} ?")
                            
                current_page = page
                current_folio = folio
                current_side = side
                page_to_file_dict[current_page] = current_filename
                
            char_count = greek_char_count(line)
            if char_count:
                page_char_counts[current_page] += greek_char_count(line)


    plt.figure(figsize=(20,10))

    vals = list(page_char_counts.values())
    mean = np.mean(vals)
    std = np.std(vals)
    print(f"Mean:                {mean:.1f}")
    print(f"Standard Deviation:  {std:.1f}")


    print("Outlier Pages:")
    warning_labels = []
    for item in page_char_counts:
        if page_char_counts[item] > mean + warning_stdev*std or page_char_counts[item] < mean - warning_stdev*std:
            print(item, page_char_counts[item], page_to_file_dict[item], sep='\t\t')
            warning_labels.append( item )

    labels, values = zip(*page_char_counts.items())

    x_labels = []
    for index, label in enumerate(labels):
        if index % 20 == 0:
            x_labels.append(label)
        else:
            x_labels.append("")

    warning_annotations = []
    for index, label in enumerate(labels):
        if label in warning_labels:
            warning_annotations.append(label)
        else:
            warning_annotations.append("")

    indexes = np.arange(len(labels))
    plt.scatter(indexes, values, marker='o', edgecolor='red', facecolor='#00000000', linewidths=1)

    for outlier in warning_labels:
        index = labels.index(outlier)
        plt.annotate(outlier, (indexes[index], values[index]))

    plt.ylabel("Greek characters on folio side", horizontalalignment='right', y=1.0)
    plt.xlabel("Folio side", horizontalalignment='right', x=1.0)

    plt.xticks(indexes + 0.5, x_labels)
    if show or output_path is None:
        plt.show()

    if output_path:
        output_path = Path(output_path)
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, bbox_inches='tight')
        print("Saved plot to:", output_path)

            
            
def read_sentence_counts( filename_prefix, start_homily = 0, end_homily = 32 ):
    sentence_counts = defaultdict( lambda: defaultdict(lambda: defaultdict(int)))

    for homily_index in range(start_homily, end_homily+1):
        homily_index = int(homily_index)
        filename = f"{filename_prefix}{homily_index}"
        filename_leadingzero = f"{filename_prefix}0{homily_index}"
    
        f, _ = try_open_file( [ filename, filename_leadingzero, filename + ".txt", filename_leadingzero + ".txt"])
        if not f:
            print("Cannot open", filename)
            continue

        data = f.read()

        paragraphs = re.findall("\<P ([0-9]+)\>(.*?)\<\/P\>", data, re.MULTILINE|re.DOTALL)
        for paragraph in paragraphs:
            paragraph_number = int(paragraph[0])
            paragraph_text = paragraph[1]

            sentences = re.findall("\<S ([0-9]+)\>(.*?)\<\/S\>", paragraph_text, re.MULTILINE|re.DOTALL)
            for sentence in sentences:
                sentence_number = int(sentence[0])
                sentence_counts[homily_index][paragraph_number][sentence_number] = greek_char_count(sentence[1].strip())

    return sentence_counts


def length_dict_dataframe( sentence_counts ):
    count = 0
    for h in sentence_counts:
        for p in sentence_counts[h]:
            for s in sentence_counts[h][p]:
                count +=1
    return count


def compare_dataframes(sentence_counts_base, sentence_counts_comparison, threshold):
    for h in sentence_counts_base:
        if h not in sentence_counts_comparison:
            print(f"Homily {h} not found in comparison text.")
            continue
        for p in sentence_counts_base[h]:
            if p not in sentence_counts_comparison[h]:
                print(f"Paragraph {h}.{p} not found in comparison text.")
                continue        
            for s in sentence_counts_base[h][p]:
                if s not in sentence_counts_comparison[h][p]:
                    print(f"Sentence {h}.{p}.{s} not found in comparison text.")
                    continue
                # ignore if the base text is empty                
                if sentence_counts_base[h][p][s] == 0:
                    continue
                if sentence_counts_comparison[h][p][s] == 0:
                    print(f"Sentence {h}.{p}.{s} is empty in comparison text.")
                
                if sentence_counts_comparison[h][p][s] > sentence_counts_base[h][p][s] + threshold:
                    print(f"Sentence {h}.{p}.{s} above the threshold.")


def write_square( dwg, position, colour, size=1 , height=10):
    dwg.add(dwg.rect( (position*size, 0), ( (position+1) * size, height ), fill=colour ))


def svg_dataframes( sentence_counts_base,  sentence_counts_comparison, threshold, filename, size=1, height=10):
    """Write the comparison of two sentence counts to an SVG file."""
    print("Writing SVG file:", filename)
    
    count = length_dict_dataframe(sentence_counts_base)
    dwg = svgwrite.Drawing(filename, size=(count*size,height), profile='tiny')
    
    position = 0
    for h in sentence_counts_base:
        for p in sentence_counts_base[h]:
            for s in sentence_counts_base[h][p]:
                # ignore if the base text is empty                
                if sentence_counts_base[h][p][s] == 0:
                    continue
                colour = ""
                if h not in sentence_counts_comparison or p not in sentence_counts_comparison[h] or s not in sentence_counts_comparison[h][p]:
                    colour = "black"
                elif sentence_counts_comparison[h][p][s] == 0:
                    colour = "red"
                elif sentence_counts_comparison[h][p][s] > sentence_counts_base[h][p][s] + threshold:
                    colour = "blue"
                else:
                    colour = "green"

                write_square( dwg, position, colour, size)
                position += size
                
    dwg.save()            
    

def compare_counts(base_prefix:str, comparison_prefix:str, output_svg:Path=None, start_homily:int=0, end_homily=32, threshold:int=50):
    print("Reading Base:")
    sentence_counts_base = read_sentence_counts(base_prefix, start_homily, end_homily)

    count = length_dict_dataframe(sentence_counts_base)
    print('Base Sentence Count:', count)

    print("Reading Comparison:")
    sentence_counts_comparison = read_sentence_counts(comparison_prefix, start_homily, end_homily)

    print("Checking:")
    compare_dataframes(sentence_counts_base, sentence_counts_comparison, threshold)
    
    if output_svg:
        svg_dataframes(sentence_counts_base, sentence_counts_comparison, threshold, output_svg)
