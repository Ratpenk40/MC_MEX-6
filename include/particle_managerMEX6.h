#ifndef particle3D_manager_MEX6_header
#define particle3D_manager_MEX6_header

#include<iostream>
#include "particleMEX63D.h"
#include <boost/python.hpp>

typedef std::vector<double> MyList;

class particle3D_managerMEX6{
    
    public:
    particle3D_managerMEX6();
    particle3D_managerMEX6(int particles);
    ~particle3D_managerMEX6();
    
    void Move(double, double, double, boost::python::list&, bool, double);
    //void Shuffle(double a[][3]);

    void Shuffle(boost::python::list& );
    std::vector<double> GetXpos();
    std::vector<double> GetYpos();
    std::vector<double> GetZpos();
    std::vector<double> GetID();

    std::vector<double> vec();
    
    void SetSettings(float, float, float, float, float );

    private:
    std::vector<particleMEX63D*> list_of_particles;
    
    std::mt19937 gen;
    
};

#endif
