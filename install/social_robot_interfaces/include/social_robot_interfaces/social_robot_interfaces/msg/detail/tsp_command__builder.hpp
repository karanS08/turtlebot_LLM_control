// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from social_robot_interfaces:msg/TspCommand.idl
// generated code does not contain a copyright notice

#ifndef SOCIAL_ROBOT_INTERFACES__MSG__DETAIL__TSP_COMMAND__BUILDER_HPP_
#define SOCIAL_ROBOT_INTERFACES__MSG__DETAIL__TSP_COMMAND__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "social_robot_interfaces/msg/detail/tsp_command__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace social_robot_interfaces
{

namespace msg
{

namespace builder
{

class Init_TspCommand_waypoints
{
public:
  Init_TspCommand_waypoints()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::social_robot_interfaces::msg::TspCommand waypoints(::social_robot_interfaces::msg::TspCommand::_waypoints_type arg)
  {
    msg_.waypoints = std::move(arg);
    return std::move(msg_);
  }

private:
  ::social_robot_interfaces::msg::TspCommand msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::social_robot_interfaces::msg::TspCommand>()
{
  return social_robot_interfaces::msg::builder::Init_TspCommand_waypoints();
}

}  // namespace social_robot_interfaces

#endif  // SOCIAL_ROBOT_INTERFACES__MSG__DETAIL__TSP_COMMAND__BUILDER_HPP_
