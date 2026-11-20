Simple table with alignments:

  Right     Left     Center     Default
-------     ------ ----------   -------
     12     12        12            12
    123     123       123          123
      1     1          1             1

Table:  Simple table caption.

Headerless:

-------     ------ ----------   -------
     12     12        12             12
    123     123       123           123
-------     ------ ----------   -------

Multiline table with relative widths:

-------------------------------------------------------------
 Centered   Default           Right Left
  Header    Aligned         Aligned Aligned
----------- ------- --------------- -------------------------
   First    row                12.0 Example of a row that
                                    spans multiple lines.

  Second    row                 5.0 Here's another one. Note
                                    the blank line between
                                    rows.
-------------------------------------------------------------

Table: Here's the caption. It, too, may span
multiple lines.

Pipe table:

| Right | Left | Default | Center |
|------:|:-----|---------|:------:|
|   12  |  12  |    12   |    12  |
|  123  |  123 |   123   |   123  |

: Pipe table caption {#tbl:pipe}

Empty pipe table body:

| x   | y   |
|-----|-----|

Grid table with spans, a table head, and a table foot:

+---------------------+----------+
| Property            | Earth    |
+=============+=======+==========+
| Temperature | min   | -89.2 °C |
| 1961-1990   +-------+----------+
|             | mean  | 14 °C    |
|             +-------+----------+
|             | max   | 56.7 °C  |
+=============+=======+==========+
| Footer      | spans two cols   |
+=============+=======+==========+

: Grid table with spans.
