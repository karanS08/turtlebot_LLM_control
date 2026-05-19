// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from social_robot_interfaces:srv/Tours.idl
// generated code does not contain a copyright notice

#ifndef SOCIAL_ROBOT_INTERFACES__SRV__DETAIL__TOURS__BUILDER_HPP_
#define SOCIAL_ROBOT_INTERFACES__SRV__DETAIL__TOURS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "social_robot_interfaces/srv/detail/tours__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace social_robot_interfaces
{

namespace srv
{

namespace builder
{

class Init_Tours_Request_idx
{
public:
  Init_Tours_Request_idx()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::social_robot_interfaces::srv::Tours_Request idx(::social_robot_interfaces::srv::Tours_Request::_idx_type arg)
  {
    msg_.idx = std::move(arg);
    return std::move(msg_);
  }

private:
  ::social_robot_interfaces::srv::Tours_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::social_robot_interfaces::srv::Tours_Request>()
{
  return social_robot_interfaces::srv::builder::Init_Tours_Request_idx();
}

}  // namespace social_robot_interfaces


namespace social_robot_interfaces
{

namespace srv
{

namespace builder
{

class Init_Tours_Response_tour
{
public:
  Init_Tours_Response_tour()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::social_robot_interfaces::srv::Tours_Response tour(::social_robot_interfaces::srv::Tours_Response::_tour_type arg)
  {
    msg_.tour = std::move(arg);
    return std::move(msg_);
  }

private:
  ::social_robot_interfaces::srv::Tours_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::social_robot_interfaces::srv::Tours_Response>()
{
  return social_robot_interfaces::srv::builder::Init_Tours_Response_tour();
}

}  // namespace social_robot_interfaces

#endif  // SOCIAL_ROBOT_INTERFACES__SRV__DETAIL__TOURS__BUILDER_HPP_
