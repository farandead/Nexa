def string_with_errors(text,pos_start,pos_end):
    result = ''
    # calcuilating the indices
    index_start = max(text.rfind("\n",0,pos_start.index),0)
    index_end = text.find('\n',index_start + 1)
    if index_end < 0: index_end = len(text)

    # generate each line 
    line_count = pos_end.line_num - pos_start.line_num + 1

    for i in range(line_count):
        line = text[index_start:index_end]
        column_start = pos_start.col if i == 0 else 0
        column_end = pos_end.col if i == line_count - 1 else len(line) -1

        # adding to the results 
        result += line + '\n'
        result += " " * column_start + '^' * (column_end - column_start)

        # recalulating the indices 
        index_start = index_end
        index_end = text.find("\n", index_start + 1)
        if index_end < 0 :index_end = len(text)

    return result.replace('\t','')



