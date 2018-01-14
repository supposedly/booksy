import { Component, OnInit } from '@angular/core';

import { MemberService } from '../member.service';

import { Globals } from '../globals';

@Component({
  selector: 'app-my-items',
  templateUrl: './my-items.component.html',
  styleUrls: ['./my-items.component.css']
})
export class MyItemsComponent implements OnInit {
  msg: string = '';
  items: any[] = [];
  cont: number = 0; // should remain unused here, I think, because one wouldn't really have so many holds/items as to require pagination
  
  constructor(
    public globals: Globals,
    private memberService: MemberService
  ) { }

  ngOnInit() {
    this.getItems();
  }
  
  getItems() {
    this.memberService.getItems()
      .subscribe(resp => this.items = resp, err => this.msg = err.error?err.error:'Error.')
  }

}
