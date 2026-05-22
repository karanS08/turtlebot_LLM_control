// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from social_robot_interfaces:msg/TspCommand.idl
// generated code does not contain a copyright notice

#ifndef SOCIAL_ROBOT_INTERFACES__MSG__DETAIL__TSP_COMMAND__STRUCT_HPP_
#define SOCIAL_ROBOT_INTERFACES__MSG__DETAIL__TSP_COMMAND__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__social_robot_interfaces__msg__TspCommand __attribute__((deprecated))
#else
# define DEPRECATED__social_robot_interfaces__msg__TspCommand __declspec(deprecated)
#endif

namespace social_robot_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct TspCommand_
{
  using Type = TspCommand_<ContainerAllocator>;

  explicit TspCommand_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
  }

  explicit TspCommand_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
    (void)_alloc;
  }

  // field types and members
  using _waypoints_type =
    std::vector<int64_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int64_t>>;
  _waypoints_type waypoints;

  // setters for named parameter idiom
  Type & set__waypoints(
    const std::vector<int64_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int64_t>> & _arg)
  {
    this->waypoints = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    social_robot_interfaces::msg::TspCommand_<ContainerAllocator> *;
  using ConstRawPtr =
    const social_robot_interfaces::msg::TspCommand_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<social_robot_interfaces::msg::TspCommand_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<social_robot_interfaces::msg::TspCommand_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      social_robot_interfaces::msg::TspCommand_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<social_robot_interfaces::msg::TspCommand_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      social_robot_interfaces::msg::TspCommand_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<social_robot_interfaces::msg::TspCommand_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<social_robot_interfaces::msg::TspCommand_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<social_robot_interfaces::msg::TspCommand_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__social_robot_interfaces__msg__TspCommand
    std::shared_ptr<social_robot_interfaces::msg::TspCommand_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__social_robot_interfaces__msg__TspCommand
    std::shared_ptr<social_robot_interfaces::msg::TspCommand_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const TspCommand_ & other) const
  {
    if (this->waypoints != other.waypoints) {
      return false;
    }
    return true;
  }
  bool operator!=(const TspCommand_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct TspCommand_

// alias to use template instance with default allocator
using TspCommand =
  social_robot_interfaces::msg::TspCommand_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace social_robot_interfaces

#endif  // SOCIAL_ROBOT_INTERFACES__MSG__DETAIL__TSP_COMMAND__STRUCT_HPP_
