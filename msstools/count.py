from collections import Counter, defaultdict
from pathlib import Path
import regex
import numpy as np
import matplotlib.pyplot as plt

def greek_char_count(string:str) -> int:
    """Counts the number of Greek characters in a given string."""
    chars = regex.findall( '\p{IsGreek}', string  )
    return len(chars)


def count_greek_chars(
    paths:list[str|Path],
    warning_stds:float = 1.8,
    output_path:Path|None = None,
    show:bool = False,
):
    page_char_counts = Counter()
    page_to_file_dict = defaultdict(list)

    current_page = "Unk"
    current_folio = None
    current_side = None
    for path in paths:
        with open(path, 'r', encoding='utf-8') as f:
            filename = Path(path).name
            current_filename = filename

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
                            print("Folio error from %s to %s in file %s ?" % (current_page, page, current_filename) )
                        if folio != current_folio and side == current_side and side != 'p':
                            print("Folio side error from %s to %s in file %s ?" % (current_page, page, current_filename) )
                        elif folio != current_folio and side != 'r' and side != 'p':
                            print("Folio side error from %s to %s in file %s ?" % (current_page, page, current_filename) )
                                
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
    print("Mean:                %.1f" % mean)
    print("Standard Deviation:  %.1f" % std)

    print("Outlier Pages:")
    warning_labels = []
    for item in page_char_counts:
        if page_char_counts[item] > mean + warning_stds*std or page_char_counts[item] < mean - warning_stds*std:
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

            
            