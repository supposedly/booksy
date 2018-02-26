import { Component, OnInit } from '@angular/core';

import { LocationService } from '../location.service';

@Component({
  selector: 'app-location-edit',
  templateUrl: './location-edit.component.html',
  styles: ['strong { font-weight: 400; }']
})
export class LocationEditComponent implements OnInit {
  color: string = '#f7f7f7';
  initialColor: string = '#f7f7f7';
  msg: string;
  locname: string;
  checkoutpw: string = '';
  nomodify: boolean = true;
  fine_amt: number;
  fine_interval: number;
  
  constructor(private locationService: LocationService) {}
  
  ngOnInit() {
    this.locationService.getLocInfo()
      .subscribe(resp => {
        this.color = this.initialColor = resp.loc.color;
        this.locname = resp.loc.name;
        this.fine_amt = resp.loc.fine_amt;
        this.fine_interval = resp.loc.fine_interval;
      });
  }
  
  submit() {
    this.locationService.edit(this.locname, this.color, this.fine_amt, this.fine_interval, this.nomodify?null:this.checkoutpw)
      .subscribe(resp => this.msg = "Edited successfully.", err => this.msg = err.error?err.error:"Error.");
  }
}
