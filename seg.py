# 下面是分割的代码
# seg_threshold代码是用来分割单个阈值的
# seg_thresholds是用来分割多个阈值的
# 注意，我在这里只是分割，将所有分割的片段都收入其中，还没有删除那些片段长度小于100的，之后会删除
# 这后面的输出并不是数据，而是索引，是分割后每个片段的起始位置在原数据中的索引


def seg_thresholds(data, time_col, thresholds, max_len=120):
    """
    segment with thresholds
    data：传入的数据
    time_col：数据中时间列的名称：这里是 "time"
    thresholds：时间阈值，以秒为单位
    """
    data[time_col] = pd.to_datetime(data[time_col])
    diff = data[time_col].diff()[1:]
    diff = [d.total_seconds() for d in diff]
    segs = (np.where(np.array(diff) > thresholds[0])[0]+ 1).tolist()
    segs.insert(0, 0)
    segs.append(len(data))

    for j in range(1, len(thresholds)):
        segs = seg_threshold(data, time_col, segs.copy(), j, max_len)
    # by length
    new_seg = []
    for k in range(len(segs)-1):
        new_seg.append(segs[k])
        if (segs[k+1] - segs[k]) > max_len+1:
            l = segs[k+1] - segs[k]
            n = l // (max_len - 10)
            # ll = int(l/n)
            for m in range(n):
                new_seg.append(seg[k] + (m+1) * (min_max - 10))
    new_seg.append(segs[-1])
    return new_seg

def seg_threshold(data, time_col, seg, threshold, max_len=120):
    """
    segment with one threshold
    """
    indexes = (np.where(np.diff(seg) > max_len)[0] + 1).tolist()
    if len(indexes)>0:
        data[time_col] = pd.to_datetime(data[time_col])
        seg_appends = [seg[0]]
        for j in range(len(seg)-1):
            if (seg[j+1] - seg[j]) > max_len:
                data_seg = data.loc[seg[j]:seg[j+1]-1, :]
                data_seg.reset_index(drop=True, inplace=True)
                data_seg_time_diff = data_seg[time_col].diff()[1:]
                data_seg_time_diff = [d.total_seconds() for d in data_seg_time_diff]
                seg_index = (np.where(np.array(data_seg_time_diff) > threshold)[0] + 1).tolist()
                if len(seg_index) > 0:
                    seg_append = [0]
                    for l in seg_index:
                        if (l - seg_append[-1]) > max_len:
                            seg_append.append(l)
                    if len(data_seg) - seg_append[-1] < max_len:
                        seg_apppend = seg_append[:-1]
                    seg_append = seg_append[1:]
                    seg_append = [a + seg[j] for a in seg_append]
                    seg_appends.extend(seg_append)
                seg_appends.append(seg[j+1])
            else:
                seg_appends.append(seg[j+1])
        return seg_appends
    else:
          return seg
