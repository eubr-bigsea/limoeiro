class DataCollectionDiffChecker:
    """Class to implement the collection data engine."""

    def __init__(self, log):
        self.log = log

    def _diff_list(self, k, new_dict, current_dict, obj_type):
        """Method to do a diff check between two list objects."""
        diff = False

        # Iterate over the new values and search for their match in the old values.
        for new in new_dict[k]:
            match = False
            for current in current_dict[k]:
                # Find the elements with the same name.
                if new["name"] == current["name"]:
                    match = True
                    for n in new.keys():
                        # Check if there was any difference.
                        if new[n] != current[n]:
                            diff = True
                            # Log the difference found.
                            self.log.log_diff_list_element(
                                obj_type,
                                current_dict["id"],
                                current_dict["fully_qualified_name"],
                                k,
                                n,
                                current[n],
                                new[n],
                            )

            if match is False:
                # If there is no match, an new element was added.
                diff = True

                # Log the difference found.
                self.log.log_element_added(
                    obj_type,
                    current_dict["id"],
                    current_dict["fully_qualified_name"],
                    k,
                    new["name"],
                )

        # Iterate over the old values and search for their match in
        # the new values.
        for current in current_dict[k]:
            match = any(new["name"] == current["name"] for new in new_dict[k])

            if match is False:
                # If there is no match, an new element was removed.
                diff = True

                # Log the difference found.
                self.log.log_element_removed(
                    obj_type,
                    current_dict["id"],
                    current_dict["fully_qualified_name"],
                    k,
                    current["name"],
                )

        return diff

    def _diff_element(self, k, new_dict, current_dict, obj_type):
        """Method to do a diff check between two elements."""
        new_value = new_dict[k]
        diff = False
        if "_id" in k:
            # If it is an id object, access the object to get its id.
            key_obj = k.replace("_id", "")
            if key_obj not in current_dict:
                return False
            current_value = current_dict[key_obj]["id"]
        else:
            current_value = current_dict[k]

        if new_value != current_value:
            diff = True
            # Log the difference found.
            self.log.log_diff_field(
                obj_type,
                current_dict["id"],
                current_dict["fully_qualified_name"],
                k,
                current_value,
                new_value,
            )

        return diff

    def diff_objects(self, new_dict, current_dict, obj_type):
        """Method to do a diff check between two objects, and return the object
        with the new values replaced."""
        result_dict = current_dict

        diff = False
        for k in new_dict.keys():
            new_value = new_dict[k]

            if isinstance(new_dict[k], list):
                # If the element is a list, check a list diff
                diff |= self._diff_list(k, new_dict, current_dict, obj_type)
            else:
                # If the element is an _element, check a _element diff
                diff |= self._diff_element(k, new_dict, current_dict, obj_type)

            # Always overwrite the current value with the new value.
            result_dict[k] = new_value

        if diff:
            # If there was a difference, increment the version of the object
            current_version = result_dict["version"]
            version_arr = current_version.split(".")
            new_version = ".".join(
                [str(int(version_arr[0]) + 1), version_arr[1], version_arr[2]]
            )
            result_dict["version"] = new_version

        return result_dict
