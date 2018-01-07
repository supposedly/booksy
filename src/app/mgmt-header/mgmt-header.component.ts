import { Component, OnInit, Input } from '@angular/core';

import { MgmtHeaderButtonService } from '../mgmt-header-button.service';

import { NavButton } from '../classes';

@Component({
  selector: 'app-mgmt-header',
  templateUrl: './mgmt-header.component.html',
  styleUrls: ['./mgmt-header.component.css']
})
export class MgmtHeaderComponent /*implements OnInit*/ {
  buttons: NavButton[] = null;
  
  constructor(
    private buttonService: MgmtHeaderButtonService,
  ) {}
  
  @Input() uID: string;
  
  ngOnChanges() {
    this.getButtons();
  }
  
  /*
  ngOnInit() {
    this.getButtons();
  }
  */
  
  getButtons(): void {
    if (!this.buttons) {
      this.buttonService.getButtons(this.uID)
        .subscribe(buttons => this.buttons = buttons);
    }
  }

}
