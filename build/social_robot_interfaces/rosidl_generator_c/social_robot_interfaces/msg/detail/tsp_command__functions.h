// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from social_robot_interfaces:msg/TspCommand.idl
// generated code does not contain a copyright notice

#ifndef SOCIAL_ROBOT_INTERFACES__MSG__DETAIL__TSP_COMMAND__FUNCTIONS_H_
#define SOCIAL_ROBOT_INTERFACES__MSG__DETAIL__TSP_COMMAND__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "social_robot_interfaces/msg/rosidl_generator_c__visibility_control.h"

#include "social_robot_interfaces/msg/detail/tsp_command__struct.h"

/// Initialize msg/TspCommand message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * social_robot_interfaces__msg__TspCommand
 * )) before or use
 * social_robot_interfaces__msg__TspCommand__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_social_robot_interfaces
bool
social_robot_interfaces__msg__TspCommand__init(social_robot_interfaces__msg__TspCommand * msg);

/// Finalize msg/TspCommand message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_social_robot_interfaces
void
social_robot_interfaces__msg__TspCommand__fini(social_robot_interfaces__msg__TspCommand * msg);

/// Create msg/TspCommand message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * social_robot_interfaces__msg__TspCommand__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_social_robot_interfaces
social_robot_interfaces__msg__TspCommand *
social_robot_interfaces__msg__TspCommand__create();

/// Destroy msg/TspCommand message.
/**
 * It calls
 * social_robot_interfaces__msg__TspCommand__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_social_robot_interfaces
void
social_robot_interfaces__msg__TspCommand__destroy(social_robot_interfaces__msg__TspCommand * msg);

/// Check for msg/TspCommand message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_social_robot_interfaces
bool
social_robot_interfaces__msg__TspCommand__are_equal(const social_robot_interfaces__msg__TspCommand * lhs, const social_robot_interfaces__msg__TspCommand * rhs);

/// Copy a msg/TspCommand message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_social_robot_interfaces
bool
social_robot_interfaces__msg__TspCommand__copy(
  const social_robot_interfaces__msg__TspCommand * input,
  social_robot_interfaces__msg__TspCommand * output);

/// Initialize array of msg/TspCommand messages.
/**
 * It allocates the memory for the number of elements and calls
 * social_robot_interfaces__msg__TspCommand__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_social_robot_interfaces
bool
social_robot_interfaces__msg__TspCommand__Sequence__init(social_robot_interfaces__msg__TspCommand__Sequence * array, size_t size);

/// Finalize array of msg/TspCommand messages.
/**
 * It calls
 * social_robot_interfaces__msg__TspCommand__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_social_robot_interfaces
void
social_robot_interfaces__msg__TspCommand__Sequence__fini(social_robot_interfaces__msg__TspCommand__Sequence * array);

/// Create array of msg/TspCommand messages.
/**
 * It allocates the memory for the array and calls
 * social_robot_interfaces__msg__TspCommand__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_social_robot_interfaces
social_robot_interfaces__msg__TspCommand__Sequence *
social_robot_interfaces__msg__TspCommand__Sequence__create(size_t size);

/// Destroy array of msg/TspCommand messages.
/**
 * It calls
 * social_robot_interfaces__msg__TspCommand__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_social_robot_interfaces
void
social_robot_interfaces__msg__TspCommand__Sequence__destroy(social_robot_interfaces__msg__TspCommand__Sequence * array);

/// Check for msg/TspCommand message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_social_robot_interfaces
bool
social_robot_interfaces__msg__TspCommand__Sequence__are_equal(const social_robot_interfaces__msg__TspCommand__Sequence * lhs, const social_robot_interfaces__msg__TspCommand__Sequence * rhs);

/// Copy an array of msg/TspCommand messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_social_robot_interfaces
bool
social_robot_interfaces__msg__TspCommand__Sequence__copy(
  const social_robot_interfaces__msg__TspCommand__Sequence * input,
  social_robot_interfaces__msg__TspCommand__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // SOCIAL_ROBOT_INTERFACES__MSG__DETAIL__TSP_COMMAND__FUNCTIONS_H_
