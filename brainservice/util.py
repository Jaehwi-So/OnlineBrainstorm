def depth_first_search(posts, parent=None, depth=0):
    result = []
    for post in posts:
        if post.arg_tree_parent == parent:
            post.arg_tree_level = depth
            result.append(post)
            children = depth_first_search(posts, parent=post, depth=depth+1)
            result.extend(children)
    return result
